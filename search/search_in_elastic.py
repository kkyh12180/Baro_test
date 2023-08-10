from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from search.pocket import pocket
from search.models import Prompt
import re

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

    def make_query(self,match_action,negative_match_action,prompt_match,negative_match):
        easy_negative={
            "match":{
                'negative_prompt':{
                    "query":"nsfw easynegative"
                }
            }
        }
        query = {"query": {"bool": {"should": [], "must_not" :[]}} }
        query["query"]["bool"]["must_not"].append(easy_negative)
        
        ln = len(match_action)
        for i in range(ln):
            query["query"]["bool"]["should"].append(match_action[i])
        n_ln = len(negative_match_action)
        for i in range(n_ln):
            query["query"]["bool"]["must_not"].append(negative_match_action[i])

        query["query"]["bool"]["should"].append(prompt_match)
        query["query"]["bool"]["must_not"].append(negative_match)

        return query

    def tokenizequery(self,prompt,negative_prompt):
        phrase_list =[]
        negative_phrase_list = []

        #positive
        tok = prompt.split(',')
        words = ""
        for tk in tok:
            if not tk:
                continue
            prompt = Prompt.objects.filter(prompt=tk)
            if not prompt:
                prompt=Prompt()
                prompt.prompt=tk
                prompt.positive_weight=1
                prompt.save()
            else:
                prompt_temp = prompt[0]
                prompt_temp.positive_weight=prompt_temp.positive_weight+1
                prompt_temp.save()
            
            if " " in tk:
                phrase = self.match_phrase("prompt",tk)
                phrase_list.append(phrase)
            else:
                words = words + " " + tk
        prompt_match_action = self.match("prompt",words)

        #negative
        tok = negative_prompt.split(',')
        words = ""
        for tk in tok:
            if not tk:
                continue
            prompt = Prompt.objects.filter(prompt=tk)
            if not prompt:
                prompt=Prompt()
                prompt.prompt=tk
                prompt.negative_weight=1
                prompt.save()
            else:
                prompt_temp = prompt[0]
                prompt_temp.negative_weight=prompt_temp.negative_weight+1
                prompt_temp.save()
            
            if " " in tk:
                phrase = self.match_phrase("negative_prompt",tk)
                negative_phrase_list.append(phrase)
            else:
                words = words + " " + tk
        negative_match_action = self.match("negative_prompt",words)

        return self.make_query(phrase_list, negative_phrase_list,prompt_match_action,negative_match_action)

    def query_to_elastic(self,prompt,negative_prompt):
        fin_query=self.tokenizequery(prompt,negative_prompt)
        result = self.es.search(index="test_image", body= fin_query, size = 300)
        id_list=[]
        for hit in result["hits"]["hits"]:
            id_list.append(hit["_source"])
        return id_list