# -*- coding: utf-8 -*-
import logging
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
from json import JSONDecoder
from mico.items import *
from mico.util.toolbox import *
from datetime import datetime
import time


class Status(object):

    def __init__(self, symbols):
        self.status = {}
        for sym in symbols:
            self.status[sym] = {'status':False, 'lastDocId':None}

    def set_status(self, symbol, status = True):
        self.status[symbol]['status'] = status

    def set_last_doc_id(self, symbol, lastDocId=0):
        self.status[symbol]['lastDocId'] = lastDocId

    def get_last_doc_id(self, symbol):
        return self.status[symbol]['lastDocId']

    def is_done(self, symbol):
        return self.status[symbol]['status']


class XueqiuSpider(scrapy.Spider):
    name = "xueqiu"
    allowed_domains = ["xueqiu.com"]
    handle_httpstatus_list = [400]
    start_urls = []

    headers = {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,ja;q=0.2,zh-TW;q=0.2'
        }

    # sort method: alpha or time
    # http://www.xueqiu.com/statuses/search.json?count=50&comment=0&symbol=SH000001&hl=0&source=all&sort=time&page=1'
    root_url = 'http://xueqiu.com/'
    next_url = 'http://www.xueqiu.com/statuses/search.json?comment=0&symbol=%s&hl=0&source=all&sort=time&page=%d'

    def __init__(self, **kwargs):
        super(XueqiuSpider, self).__init__(name='xueqiu spider', **kwargs)
        logging.info("scrapy is starting")
        # first request here to get cookie
        self.start_urls.append(self.root_url)
        self.symbols = [symbol for symbol in kwargs['symbols'].split(',')]
        self.current_symbol = None
        self.current_ticker = None
        self.page = 0
        self.max_count = 100
        self.close_down = False
        self.status_tracker = Status(self.symbols)

    def __close_down(self):
        for key in self.status_tracker.status.keys():
            if not self.status_tracker.is_done(key):
                return False
        return True

    def __generate_next_url(self):
        if self.current_symbol and not self.status_tracker.is_done(self.current_symbol):
            self.page += 1
        else:
            try:
                self.current_symbol = self.symbols.pop()
                self.current_ticker = TickerConversion.get_ticker(self.current_symbol)
                self.page = 1
            except IndexError:
                return None  # None return if no symbols
        url = self.next_url % (self.current_ticker, self.page)
        logging.info(url)
        return url

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, headers=self.headers, meta={'spider': 'xueqiu'})

    def parse(self, response):
        if response.status == 400:
            logging.warning("get response failure due to 400")
        elif response.status == 200:
            if response.url == self.root_url:
                pass  # do nothing, just save cookie
            else:
                js = response.body.decode('utf-8')
                comment_obj = JSONDecoder(encoding='utf-8').decode(js)
                for l in comment_obj['list']:
                    item = XueQiuCommentItem()
                    item['id'] = l['id']
                    item['text'] = l['text']
                    item['created_at'] = l['created_at']
                    item['symbol'] = response.meta['symbol']
                    item['ticker'] = response.meta['ticker']
                    yield item

                    #author_item = XueQiuAuthorItem()
                    #author_item['user_id'] = l['user']['id']
                    #author_item['screen_name'] = l['user']['screen_name']
                    #yield author_item

            next_url = self.__generate_next_url()
            if next_url:
                r = Request(next_url, dont_filter=True, headers=self.headers,
                            meta={'spider': 'xueqiu', 'ticker': self.current_ticker, 'symbol': self.current_symbol})
                yield r

        if self.__close_down():
            raise CloseSpider(reason="endpoint reached")