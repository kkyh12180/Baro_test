from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from search.pocket import pocket

class QueryMake():
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

    def match_phrase(self,positive,phrase):
        actions = {
            "match_phrase": {
                positive: {
                    "query": phrase,
                    "slop": 1
                }
            }
        }
        return actions

    def match(self,positive,words):    
        actions = {
            "match": {
                positive: {
                    "query": words                
                }
            }
        }

        return actions

    def make_query(self,match_action,prompt_match,negative_match):
        query = {"query": {"bool": {"should": [{"match":{'negative_prompt':"nsfw easynegative"}}]}}}
        ln = len(match_action)
        for i in range(ln):
            query["query"]["bool"]["should"].append(match_action[i])

        query["query"]["bool"]["should"].append(prompt_match)
        query["query"]["bool"]["should"].append(negative_match)

        return query

    def tokenizequery(self,prompt,negative_prompt):
        phrase_list =[]
        words = ""
        #positive
        prompt = prompt.replace(', ', ',')
        tok = prompt.split(',')
        for tk in tok:
            if " " in tk:
                phrase = self.match_phrase("prompt",tk)
                phrase_list.append(phrase)
            else:
                words = words + " " + tk
        prompt_match_action = self.match("prompt",words)

        words = ""
        #negative
        negative_prompt = negative_prompt.replace(', ', ',')
        tok = negative_prompt.split(',')
        for tk in tok:
            if " " in tk:
                phrase = self.match_phrase("negative_prompt",tk)
                phrase_list.append(phrase)
            else:
                words = words + " " + tk
        negative_match_action = self.match("negative_prompt",words)

        return self.make_query(phrase_list,prompt_match_action,negative_match_action)

    def query_to_elastic(self,prompt,negative_prompt):
        fin_query=self.tokenizequery(prompt,negative_prompt)
        print(fin_query)
        result = self.es.search(index="test_image", body= fin_query, size = 3)
        id_list=[]
        for hit in result["hits"]["hits"]:
            id_list.append(hit["_id"])
        return id_list
        

