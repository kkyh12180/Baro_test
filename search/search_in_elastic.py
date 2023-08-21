from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from search.pocket import pocket
from search.models import Prompt
from images.models import *
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

        self.index_name = "test_image_prompt"

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
    
    def make_query(self,match_action,negative_match_action):
        easy_negative={
            "match":{
                'negative_prompt':{
                    "query":"nsfw easynegative"
                }
            }
        }
        #특정 구문의 검색점수를 낮추기 위해서 사용
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
        
        query = {"query": {"bool": {"must": [], "must_not" :[], "should":[]}} }
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
            query["query"]["bool"]["must_not"].append(negative_match_action[i])

        return query

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

    def query_to_elastic(self,prompt,negative_prompt):
        fin_query=self.tokenizequery(prompt,negative_prompt)        
        try:
            result = self.es.search(index=self.index_name, body= fin_query, size = 300, timeout = "60s")
            id_list = [hit["_id"] for hit in result["hits"]["hits"]]
            data_list = ImageTable.objects.filter(image_id__in=id_list)
        except:
            data_list = ImageTable.objects.filter(image_id="I")
        return data_list
    
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