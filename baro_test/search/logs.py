import logging
import logstash
from elasticsearch import Elasticsearch

from search.pocket import pocket

def logs():
    info = pocket()
    host=info.es_host.replace("http://","")
    print(host)
    port=info.es_port
    es_username = info.es_username
    es_password = info.es_password

    logger = logging.getLogger('python-logstash-logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(logstash.LogstashHandler(host,port,version=1))

    logger.info('This is a test log message.')
    
    print(logger)
    print(host)

    es=Elasticsearch(
        [f"{info.es_host}:{port}"],
        http_auth=(es_username,es_password),
        )

    dashboard_query = {
        'attributes':{
            'title':'My Dashboard'
        },
        'panelsJSON':'[]',
        'refreshInterval':{'display':'Off','pause':False,'value':0},
        'timeRestore':False
    }

    response = es.index(index='.kibana',body=dashboard_query)
    if response['result'] == 'created':
        print('Dashboard created succesfully.')
    else:
        print('Failed to creat dashboard.')