import logging
import logstash
from elasticsearch import Elasticsearch

from search.pocket import pocket
from search.models import *

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

    def log_data(self,prompt,negative,user_pk):
        user = User.objects.get(user_id=user_pk)
        Prompt_log.objects.create(user=user,prompt=prompt,negative_prompt=negative)
        count=Prompt_log.objects.filter(user_id=user_pk).count()
        query={
            "prompt":prompt,
            "negative":negative
        }
        id=str(user_pk)+str(count)
        print(id)
        self.es.index(index=self.index_name,id=id,body=query)

    def logs(self,user_pk):
        prompt_logs = Prompt_log.objects.filter(user_id=user_pk)
        query={
            "query":{
                "match_all": {}
            }
        }
        res = self.es.search(index=self.index_name, body=query, size = 100)

        data=[hit['_source'] for hit in res['hits']['hits']]

        print(data)