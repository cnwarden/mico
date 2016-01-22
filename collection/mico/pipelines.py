# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from mico.items import *
import logging
from datetime import datetime
import time
from dateutil.tz import tzoffset

class XueQiuCommentPipeline(object):

    def __init__(self):
        self.es_client = Elasticsearch(settings['ES_HOST'])
        self.es_client.indices.create(settings['ES_INDEX'], ignore=400)
        self.count = 0
        self.last_doc_id = 0

        dt = datetime.now(tz=tzoffset(name='china', offset=28800))
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
            doc_body = {
                'instrument':
                    {
                        'code': item['code'],
                        'name': item['name']
                    }
            }
            self.es_client.create(index=settings['ES_REF_INDEX'], doc_type="instrument", id=item['code'], body=doc_body, ignore=(409))
        return item


class TimeSeriesPipeline(object):

    bulk_throttle = 1000

    status = {}

    actions = []

    def __init__(self):
        self.es_client = Elasticsearch(settings['ES_HOST'])
        self.es_client.indices.create(settings['ES_TIMESERIES_INDEX'], ignore=400)

    def __init_status(self, code, last_time):
        self.status[code] = { 'time': last_time, 'complete': False}

    def __set_complete(self, code, complete=True):
        self.status[code]['complete'] = complete

    def __check_all_complete(self):
        for key in self.status.keys():
            if self.status[key]['complete'] == False:
                return False
        return True

    def __query_last_time(self, code):
        search_body = {
            'size': 1,
            'query':
                {
                    'match':
                        { 'code': code}
                },
            'sort':
                {
                    'time':
                        { 'order': 'desc' }
                }
        }
        doc = self.es_client.search(index=settings['ES_TIMESERIES_INDEX'], doc_type='daily', body=search_body, ignore=(400))
        if not doc.has_key('status') and len(doc['hits']['hits'])==1 and doc['hits']['hits'][0]['_source']['time']:
            return doc['hits']['hits'][0]['_source']['time']
        else:
            return 0

    def _bulk(self):
        if len(self.actions) > 0:
            helpers.bulk(self.es_client, actions=self.actions)
            self.actions = []

    def process_item(self, item, spider):
        if isinstance(item, TimeSeriesAdminStartItem):
            last_time = self.__query_last_time(item['code'])
            self.__init_status(item['code'],last_time)
        elif isinstance(item, TimeSeriesItem):
            if item['time'] <= self.status[item['code']]['time']:
                self._bulk()
                self.__set_complete(item['code'])
                return #no need process more, better raise DropItem exception

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
            action_body = {
                '_index': settings['ES_TIMESERIES_INDEX'],
                '_type': 'daily',
                '_id': uuid,
                '_source': doc_body
            }
            self.actions.append(action_body)

            #throttle
            if len(self.actions) > self.bulk_throttle:
                self._bulk()
        elif isinstance(item, TimeSeriesAdminEndItem):
            self._bulk()

        return item
