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

    def is_float(self,str):
        try:
            float(str)
            return True
        except ValueError:
            return False
    
    # Elasticsearch에 bulk로 데이터 색인
    def index_data_to_elasticsearch(self,prompt):
        #frequency 담을 dictionary 생성
        term_freq_dic ={}

        search_body = {
            "query": {
                "match_all": {}
            },
            "size": 3000,
            "sort": [
                {"_doc": {"order": "desc"}}
            ]
        }

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
        
        no_dic = ['detailed','and','best','a','the','of','in','detail','masterpiece','with','at','up','by','very','perfect','to','is','on',]
        data_list = []
        # 상위 100개의 아이템을 출력합니다.
        n = 100
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

        # print(top_100_items)
        print(data_list)
        return data_list[:10]