# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from elasticsearch import Elasticsearch
from mico.items import *
import logging
from datetime import datetime
import time
from dateutil.tz import tzoffset
from pytz import timezone, utc

class XueQiuCommentPipeline(object):

    def __init__(self):
        self.es_client = Elasticsearch(settings['ES_HOST'])
        self.es_client.indices.create(settings['ES_INDEX'], ignore=400)
        self.count = 0
        self.last_doc_id = 0

        dt = datetime.now(tz=tzoffset(name='china', offset=28800))
        #dt = timezone('Asia/Shanghai').localize(datetime.now())
        zero_dt = datetime(dt.year, dt.month, dt.day)
        self.limit_today = time.mktime(zero_dt.timetuple())
        logging.info("today 00:00:00 = %d" % (time.mktime(zero_dt.timetuple())))

        # query last doc id
        query_body = {'size':1, 'query': {'match_all': {}}, 'sort': [{'comment.id': {'order': 'desc'}}]}
        doc = self.es_client.search(index=settings['ES_INDEX'], doc_type="comment", body=query_body, ignore=400)
        if not doc.has_key('status'):
            self.last_doc_id = doc['hits']['hits'][0]['_source']['comment']['id']
        logging.info("last doc_id:%d" % (self.last_doc_id))

    def process_item(self, item, spider):
        if isinstance(item, XueQiuCommentItem):

            if self.last_doc_id >= item['id']:
                spider.close_down = True
                raise DropItem("duplicated comment items")

            dt_str = datetime.fromtimestamp(item['created_at']/1000, tz=tzoffset(name='china', offset=28800)).strftime("%Y-%m-%d %H:%M:%S")
            doc_body = {'comment': {'id': item['id'], 'text': item['text'], 'created_at': item['created_at'], 'created_at_str': dt_str}}
            self.es_client.create(index=settings['ES_INDEX'], doc_type="comment", id=item['id'], body=doc_body, ignore=(409))

            self.count += 1
            if self.count > spider.max_count:
                spider.close_down = True

            if item['created_at'] < self.limit_today:
                spider.close_down = True
        else:
            if spider.close_down:
                raise DropItem("duplicated other following items")

        return item


class XueQiuAuthorPipeline(object):

    def __init__(self):
        self.es_client = Elasticsearch(settings['ES_HOST'])
        self.es_client.indices.create(settings['ES_INDEX'], ignore=400)

        self.last_doc_id = 0

    def process_item(self, item, spider):
        if isinstance(item, XueQiuAuthorItem):
            author_body = {'doc': {'author': {'uid': item['user_id'], 'name': item['screen_name']}}}
            self.es_client.update(index=settings['ES_INDEX'], doc_type="comment", id=self.last_doc_id, body=author_body)
        if isinstance(item, XueQiuCommentItem):
            self.last_doc_id = item['id']
        return item


#

class ReferencePipeline(object):

    def __init__(self):
        self.es_client = Elasticsearch(settings['ES_HOST'])
        self.es_client.indices.create(settings['ES_REF_INDEX'], ignore=400)

    def process_item(self, item, spider):
        if isinstance(item, ReferenceItem):
            doc_body = {'instrument': {'code': item['code'], 'name': item['name']}}
            self.es_client.create(index=settings['ES_REF_INDEX'], doc_type="instrument", id=item['code'], body=doc_body, ignore=(409))
        return item


class TimeSeriesPipeline(object):

    last_time = 0

    def __init__(self):
        self.es_client = Elasticsearch(settings['ES_HOST'])
        self.es_client.indices.create(settings['ES_TIMESERIES_INDEX'], ignore=400)
        search_body = {
            'size': 1,
            'query':
                {
                    'match':
                        { 'code': '000001'}
                },
            'sort':
                {
                    'time':
                        { 'order': 'desc' }
                }
        }
        doc = self.es_client.search(index=settings['ES_TIMESERIES_INDEX'], doc_type='daily', body=search_body, ignore=(400))
        if not doc.has_key('status') and len(doc['hits']['hits'])==1 and doc['hits']['hits'][0]['_source']['time']:
            self.last_time = doc['hits']['hits'][0]['_source']['time']
        pass

    def process_item(self, item, spider):
        if isinstance(item, TimeSeriesItem):
            if item['time'] <= self.last_time:
                spider.close_down = True
                return item

            doc_body = {
                'code': item['code'],
                'time': item['time'],
                'highprc': item['highprc'],
                'lowprc': item['lowprc'],
                'openprc': item['openprc'],
                'closeprc': item['closeprc'],
                'time_str': datetime.strftime(datetime.fromtimestamp(item['time']), '%Y-%m-%d')
            }
            uuid = "%s_%d" % (item['code'], item['time'])
            self.es_client.create(index=settings['ES_TIMESERIES_INDEX'], doc_type='daily', id=uuid, body=doc_body, ignore=(409))

        return item
