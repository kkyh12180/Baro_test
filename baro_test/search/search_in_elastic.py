from elasticsearch import Elasticsearch
import ssl
from elasticsearch.helpers import bulk
from pocket import pocket
#정보저장
info = pocket()

# Elasticsearch 연결 정보
es_host = info.es_host
es_port = info.es_port
es_username = info.es_username
es_password = info.es_password

 # Elasticsearch 클라이언트 생성
es = Elasticsearch(
    [f"{es_host}:{es_port}"],
    http_auth=(es_username, es_password),
    scheme="http"    
)


query = "red hair, upper body, eye, black"


def tokenizequery(query):
    query = query.replace(', ', ',')
    tok = query.split(',')
    phrase_list =[]
    words = ""
    for tk in tok:
        if " " in tk:
            phrase = match_phrase(tk)
            phrase_list.append(phrase)
        else:
            words = words + " " + tk

    match_action = match(words)
    return phrase_list, match_action


def match_phrase(phrase):
    actions = {
        "match_phrase": {
            "prompt": {
                "query": phrase,
                "slop": 1
            }
        }
    }

    return actions

def match(words):    
    actions = {
        "match": {
            "prompt": {
                "query": words                
            }
        }
    }

    return actions

def make_query(match_action,match):
    query = {
        "query": {
            "bool": {
                "should": [
                    
                ]                
            }
        }
    }
    ln = len(match_action)
    for i in range(ln):
        query["query"]["bool"]["should"].append(match_action[i])

    query["query"]["bool"]["should"].append(match)

    return query

# query = {"query":{"match_phrase":{"prompt":{"query": "black eyes", "slop":1}}}}


 
def query_to_elastic(query):
    phrase_list, match_action = tokenizequery(query)
    # print(phrase_list)
    # print(match_action)

    fin_query=make_query(phrase_list, match_action)
    print(fin_query)

    result = es.search(index="test_image", body= fin_query, size = 3)
    for hit in result["hits"]["hits"]:
        print(hit["_id"])


if __name__ == "__main__":
    query_to_elastic(query)
