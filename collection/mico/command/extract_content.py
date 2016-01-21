# coding:utf-8

from elasticsearch import Elasticsearch
import codecs
import re

fp = codecs.open('out.txt', mode='w', encoding='utf-8')

client = Elasticsearch([{'host':'10.35.22.80','port':9200}])
query_body = {'size':10, 'query': {'match_all': {}}, 'sort': [{'comment.id': {'order': 'desc'}}]}
doc = client.search(index='xueqiu', doc_type="comment", body=query_body, ignore=400)
for item in doc['hits']['hits']:
    text = item['_source']['comment']['text']
    text = re.sub('<.*?>', '', text)
    text = re.sub('&nbsp;', '', text)

    m = re.search('\$.*?\$', text)
    text = re.sub('\$.*\$', '', text)
    text = re.sub('^\s.*?', '', text)
    print text

    fp.write(text)
    fp.write('\n')

fp.close()
