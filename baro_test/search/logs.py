import logging
import logstash
from elasticsearch import Elasticsearch

from search.pocket import pocket

class LogClass():
    def __init__(self):
        info = pocket()
        host=info.es_host
        port=info.es_port
        es_username = info.es_username
        es_password = info.es_password

        self.es=Elasticsearch(
            [f"{host}:{port}"],
            http_auth=(es_username, es_password),
        )
        self.index_name = "log"

    def log_data(self,prompt,negative):
        query={
            "prompt":prompt,
            "negative":negative
        }
        res = self.es.index(index=self.index_name,body=query)

    def logs(self):
        query={
            "query":{
                "match_all": {}
            }
        }
        res = self.es.search(index=self.index_name,body=query, size = 20)

        data=[hit['_source'] for hit in res['hits']['hits']]

        print(data)