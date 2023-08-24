from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from search.pocket import pocket
from images.models import *

# 검색창에 입력한 긍,부정 프롬프트를 elasticsearch에서 검색하는 쿼리문 생성
# bool query의 must를 통해 and 연산을 수행하였다.
# @tokenizequery : ,를 기준으로 tokenize를 진행했고 tokenize된 것을 match_phrase 구문안에 넣어서 쿼리를 완성했다.


class Query():
    def __init__(self):
        #정보저장
        info = pocket()

        # Elasticsearch 연결 정보
        es_host = info.es_host
        es_port = info.es_port
        es_username = info.es_username
        es_password = info.es_password

        # Elasticsearch 클라이언트 생성
        self.es = Elasticsearch(
            [f"{es_host}:{es_port}"],
            http_auth=(es_username, es_password),
        )

        self.index_name = "test_image_prompt"

    #검색 쿼리를 위한 match_pharse문 생성
    def match_phrase(self,positive,phrase):
        actions = {
            "match_phrase": {
                positive: {
                    "query": phrase,
                    "slop": 1
                }
            }
        }
        if phrase == "":
           actions = {
            "match_phrase": {
                positive: {
                    "query": "blank",
                    "slop": 1
                }
            }
        }
        return actions
    
    #분해된 prompt를 이용하여 검색에 사용되는 query문 작성
    def make_query(self,match_action,negative_match_action):
        easy_negative={
            "match":{
                'negative_prompt':{
                    "query":"nsfw easynegative"
                }
            }
        }
        #boost를 통해 특정 구문의 검색점수를 낮추기 위해서 사용
        low_boost = {
            "match":{
                'prompt':{
                    "query":'''
                        detailed quality face 1.3 high eyes beautiful 1.2 hair and
                        best skin a the masterpiece body perfect girl 1.4
                        of ultra 1.1 1girl intricate long details light 8k
                        full in detail on black 1.5 background old dynamic
                        raw lighting with cinematic 1 at looking 0.8
                        extremely beauty resolution viewer lips delicate
                        pose ulzzang kpop shot years from pretty uhd
                        skirt legs 0.2 6500 waist focus
                        anatomy very cg shadow angle art woman
                        her top pureerosface_v1 medium lens large
                    ''',
                    "boost": 0.8
                }
            }
        }
        
        query = {"query": {"bool": {"must": [], "should":[]}} }
        query["query"]["bool"]["must"].append(easy_negative)       
        query["query"]["bool"]["should"].append(low_boost)
        
        ln = len(match_action)
        for i in range(ln):
            if match_action[i]["match_phrase"]["prompt"]["query"] == "blank":
                continue            
            query["query"]["bool"]["must"].append(match_action[i])

        n_ln = len(negative_match_action)
        for i in range(n_ln): 
            if negative_match_action[i]["match_phrase"]["negative_prompt"]["query"] == "blank":
                continue                       
            query["query"]["bool"]["must"].append(negative_match_action[i])

        return query

    #prompt르ㄹ 분해하여 저장
    def tokenizequery(self,prompt,negative_prompt):
        phrase_list =[]
        negative_phrase_list = []

        #positive
        tok = prompt.lower().split(',')        
        for tk in tok:
            if not tk:
                continue    
            phrase = self.match_phrase("prompt",tk)
            phrase_list.append(phrase)                            

        #negative
        tok = negative_prompt.lower().split(',')        
        for tk in tok:
            if not tk:
                continue         
            phrase = self.match_phrase("negative_prompt",tk)
            negative_phrase_list.append(phrase)           
        

        return self.make_query(phrase_list, negative_phrase_list)
    
    #query의 결과중 image_id만을 찾아서 리스트에 넣고 리턴시킨다.
    def query_to_elastic(self,prompt,negative_prompt):
        fin_query=self.tokenizequery(prompt,negative_prompt)                
        try:
            result = self.es.search(index=self.index_name, body= fin_query, size = 300, timeout = "60s")
            id_list = [hit["_id"] for hit in result["hits"]["hits"]]
            data_list = ImageTable.objects.filter(image_id__in=id_list)
        except:
            data_list = ImageTable.objects.filter(image_id="I")
        return data_list
    
    #elastic에 올라가 있는 document 삭제
    def delete_document(self, doc_id):
        index_name = self.index_name
        try:
            response = self.es.delete(index=index_name, id=doc_id)
            if response['result'] == 'deleted':
                print("delete")
            else:
                print("failed")
        except Exception as e:
            print("error")
    
    # Elasticsearch에 bulk로 데이터 색인
    def index_data_to_elasticsearch(self,prompt, index_name):
        #frequency 담을 dictionary 생성
        term_freq_dic ={}

        #기간별 트렌드를 하고 싶으면 query의 match_all 부분을 바꾸면 될 것 같다.
        search_body = {
            "query": {
                "match_all": {}
            },
            "size": 1000,
            "sort": [
                {"_doc": {"order": "desc"}}
            ]
        }

        search_result = self.es.search(index= index_name, body=search_body)

        # 검색된 문서들의 _id 리스트 추출
        recent_ids = [hit["_id"] for hit in search_result["hits"]["hits"]]

        # mtermvectors API 실행
        response = self.es.mtermvectors(
            index=self.index_name,
            body={
                "docs": [
                    {
                        "_id": doc_id,
                        "fields": [str(prompt)]
                    }
                    for doc_id in recent_ids
                ]
            }
        )

        # Elasticsearch에 mtermvectors 실행
        if 'docs' in response:
            for doc in response['docs']:
                if 'term_vectors' in doc:
                    term_vectors = doc['term_vectors']
                    if str(prompt) in term_vectors:
                        # 역색인 정보를 사용하여 원하는 작업을 수행합니다.
                        for term, info in term_vectors[str(prompt)]['terms'].items():                                                                  
                            if term in term_freq_dic:
                                temp = term_freq_dic.get(term)
                                term_freq_dic[term] = temp + info['term_freq']
                            else:
                                if isinstance(term,float) == True:
                                    continue
                                elif isinstance(term, int) == True:
                                    continue
                                else:                                
                                    term_freq_dic[term] = info['term_freq']                                             
                                                    
                else:
                    print(f"No term vectors found for Document ID: {doc['_id']}")        
        else:
            print("No documents found.")
        
        # frequency 값을 기준으로 딕셔너리를 빈도 값이 높은 순으로 정렬합니다.
        sorted_frequency = sorted(term_freq_dic.items(), key=lambda x: x[1], reverse=True)
        
        no_dic = ['detailed','and','best','a','the','of','in','detail','masterpiece','with','at','up','by','very','perfect','to','is','on','quality','realistic',]
        data_list = []
        # 상위 100개의 아이템을 출력합니다.
        n = 10
        count = 0
        i = 0

        while count < n and i < len(sorted_frequency):
            sf = sorted_frequency[i]
            if sf[0] in no_dic:
                i += 1
                continue

            try:
                float(sf[0])
            except:
                data_list.append(sf)
                count += 1
            i += 1
        
        return data_list
    
    #트렌드 집계는 프롬프트 데이터와 로그 데이터를 들고와서 각각의 백분율 값을 계산한 후 더하는 형태로 구상하였다.
    def trend_data(self, prompt):
        prompt_list= self.index_data_to_elasticsearch(prompt, "test_image_prompt")        
        log_list= self.index_data_to_elasticsearch(prompt, "test_prompt_log")

        temp_dict = {} 
        log_sum = 0
        prompt_sum = 0

        for i in range(len(prompt_list)):
            prompt_sum = prompt_sum + prompt_list[i][1]            
        for i in range(len(log_list)):
            log_sum = log_sum + log_list[i][1]            

        
        #키가 있으면 있는 것에 value를 집어넣고 없으면 새로운 키 생성
        for i in range(len(prompt_list)):
            if prompt_list[i][0] in temp_dict.keys():
                temp_dict[prompt_list[i][0]] = temp_dict[prompt_list[i][0]] + prompt_list[i][1]/prompt_sum
            else:
                temp_dict[prompt_list[i][0]] = prompt_list[i][1]/prompt_sum

        
        for i in range(len(log_list)):
            if log_list[i][0] in temp_dict.keys():
                temp_dict[log_list[i][0]] = temp_dict[log_list[i][0]] + log_list[i][1]/log_sum
            else:
                temp_dict[log_list[i][0]] = log_list[i][1]/log_sum
        

        sorted_frequency = sorted(temp_dict.items(), key=lambda x: x[1], reverse=True)

        return sorted_frequency
    
    #태그로 되어있는 프롬프트를 클릭하면 이 프롬프트를 가지는 리스트를 반환
    def search_to_tag(self, prompt, positive):
        search_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase":{
                                positive : {"query": prompt}
                            }
                        }
                    ]
                }              
            
            },
        
            "size": 1000,

            "sort": [
                {"_doc": {"order": "desc"}}
            ]
        }
        try:
            result = self.es.search(index= self.index_name, body=search_body)
            id_list = [hit["_id"] for hit in result["hits"]["hits"]]
            data_list = ImageTable.objects.filter(image_id__in=id_list)
        except:
            data_list = ImageTable.objects.filter(image_id="I")
        
        return data_list