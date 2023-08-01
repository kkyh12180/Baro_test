from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from search.pocket import pocket

class QueryMake():
    def __init__(self):
        info = pocket()
        # Elasticsearch 연결 정보
        es_host = info.es_host
        es_port = info.es_port
        es_username = info.es_username
        es_password = info.es_password

        self.es = Elasticsearch(
            [f"{es_host}:{es_port}"],
            http_auth=(es_username, es_password),  
        )
        self.query = {"query": {"bool": {"should": []}}}
        # 쿼리 작성
        self.query_temp=self.query['query']['bool']['should']
    
    def search(self):
        print(self.query)
        result = self.es.search(index="test_image",body=self.query,size=5)
        push_result = []
        # 검색 결과 확인
        for hit in result["hits"]["hits"]:
            temp_dict=hit["_source"]
            push_result.append(temp_dict)
            
        return push_result
    
    def query_to_elasticsearch(self):
        self.query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match_phrase": {
                                "prompt": {
                                    "query": "red hair",
                                    "slop": 1
                                }
                            }
                        },
                        {
                            "match_phrase": {
                                "prompt": {
                                    "query": "black eyes",
                                    "slop": 1
                                }
                            }
                        }
                    ]
                }
            }
        }
        return self.search()
    
    def make_match_phrase(self,positive,prompt):
        prompt_dict={"match_phrase":{positive:{"query":prompt,"slop":1}}}
        self.query_temp.append(prompt_dict)
    
    def make_match(self,positive,prompt):
        prompt_dict={"match":{positive:{"query":prompt}}}
        self.query_temp.append(prompt_dict)