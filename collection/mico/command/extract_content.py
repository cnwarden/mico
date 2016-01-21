# coding:utf-8

from elasticsearch import Elasticsearch
import codecs

fp = codecs.open('stock.dict', mode='w', encoding='utf-8')

client = Elasticsearch([{'host': '127.0.0.1', 'port': 9200}])
query_body = {
    'size': 10000,
    'query':
        {
            'match_all': {}
        },
    'sort':
        [
            {
                'instrument.code':
                    {'order': 'asc'}
             }
        ]
    }
doc = client.search(index='reference', doc_type="instrument", body=query_body, ignore=400)

for item in doc['hits']['hits']:
    text = item['_source']['instrument']['name']
    fp.write(text)
    fp.write('\n')

fp.close()
