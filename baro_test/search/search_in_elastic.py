from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from search.pocket import pocket

# Elasticsearch에
def query_to_elasticsearch():
    info = pocket()
    # Elasticsearch 연결 정보
    es_host = info.es_host
    es_port = info.es_port
    es_username = info.es_username
    es_password = info.es_password

    # 찾고 싶은 것

    # Elasticsearch 클라이언트 생성
    es = Elasticsearch(
         [f"{es_host}:{es_port}"],
        http_auth=(es_username, es_password),  
    )

    # 쿼리 작성
    query = {
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

    # Elasticsearch에 쿼리 전달, 크기도 원하는 만큼 가능하다
    result = es.search(index="test_image", body=query, size = 5)

    push_result = []
    # 검색 결과 확인
    for hit in result["hits"]["hits"]:
        temp_dict=hit["_source"]
        push_result.append(temp_dict)
        
    return push_result
