from elasticsearch import Elasticsearch

from search.pocket import pocket
from images.models import *

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
    
    # Elasticsearch에 bulk로 데이터 색인
    def index_data_to_elasticsearch(self,prompt):
        #frequency 담을 dictionary 생성
        term_freq_dic ={}

        search_body = {
            "query": {
                "match_all": {}
            },
            "size": 1000,
            "sort": [
                {"_doc": {"order": "desc"}}
            ]
        }
        #최근 1000개의 query를 가져오기
        search_result = self.es.search(index=self.index_name, body=search_body)

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
        
        #순위에서 제거하기 위한 키워드 저장
        no_dic = ['detailed','and','best','a','the','of','in','detail','masterpiece','with','at','up','by','very','perfect','to','is','on','quality','realistic',]
        data_list = []
        # 상위 20개의 아이템을 추출합니다.
        n = 20
        count = 0
        i = 0
        while count < n and i < len(sorted_frequency):
            sf = sorted_frequency[i]
            #실수 형식이거나 키워드가 no_dic에 저장되어 있을 경우 제외
            try:
                float(sf[0])
                i+=1
                continue
            except:
                if sf[0] in no_dic:
                    i += 1
                    continue
            
            data_list.append(sf)
            count += 1
            i += 1
        
        return data_list