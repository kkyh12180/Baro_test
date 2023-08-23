from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from search.pocket import pocket
from search.models import Prompt
from images.models import *
import re

class QueryRank():
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
        self.log_name = "test_prompt_log"

    def is_float(self,str):
        try:
            float(str)
            return True
        except ValueError:
            return False
    
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
        n = 20
        count = 0
        i = 0

        while count < n and i < len(sorted_frequency):
            sf = sorted_frequency[i]
            if sf[0] in no_dic or self.is_float(sf[0]):
                i += 1
                continue
            
            data_list.append(sf)
            count += 1
            i += 1
        
        return data_list
    
    #트렌드 집계는 프롬프트 데이터와 로그 데이터를 들고와서 각각의 백분율 값을 계산한 후 더하는 형태로 구상하였다.
    def trend_data(self, prompt):
        prompt_list= self.index_data_to_elasticsearch(self,prompt, "test-image-prompt")        
        log_list= self.index_data_to_elasticsearch(self,prompt, "test-prompt-log")

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
               

        
        

    
        
