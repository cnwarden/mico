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
from mico.util.esagent import *
import logging
from datetime import datetime
import time
from dateutil.tz import tzoffset
from mico.util.toolbox import TimeService, TimeHelper

class XueQiuCommentPipeline(object):

    def __init__(self):
        self.esclient = ESAgent(hosts=settings['ES_TEST_HOST'])
        self.esclient.initalize()

        self.limit_today = int(TimeHelper.get_today_epoch_time() * 1000)

    def __get_last_doc_id(self, spider, symbol):
        if spider.status_tracker.get_last_doc_id(symbol) is None:
            spider.status_tracker.set_last_doc_id(symbol, self.esclient.get_last_comment_id(symbol))

    def process_item(self, item, spider):
        if isinstance(item, XueQiuCommentItem):

            # block previous to support incresement
            self.__get_last_doc_id(spider, item['symbol'])
            if spider.status_tracker.get_last_doc_id(item['symbol']) >= item['id']:
                spider.status_tracker.set_status(item['symbol'], True)
                logging.info('[%s]last:%d now:%d' % (item['symbol'], spider.status_tracker.get_last_doc_id(item['symbol']), item['id'] ))
                return # none return to avoid log
                # raise DropItem("less than last docID")

            # block yesterday
            if item['created_at'] < self.limit_today:
                spider.status_tracker.set_status(item['symbol'], True)
                return # none return to avoid log
                # raise DropItem('earlier than today')

            self.esclient.create_comment(item.toJson())
        else:
            if spider.status_tracker.set_status(item['symbol'], True):
                raise DropItem("symbol done, block other following author items")
        # continue process
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
