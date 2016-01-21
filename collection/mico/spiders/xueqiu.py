# -*- coding: utf-8 -*-
import logging
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
from json import JSONDecoder
from mico.items import *
from datetime import datetime
import time


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
    next_url = 'http://www.xueqiu.com/statuses/search.json?comment=0&symbol=SH000001&hl=0&source=all&sort=time&page=%d'

    # status flags
    close_down = False
    max_count = 100
    page = 0

    def __init__(self, **kwargs):
        super(XueqiuSpider, self).__init__(name='xueqiu spider', **kwargs)
        logging.info("scrapy is starting")
        # first request here to get cookie
        self.start_urls.append(self.root_url)

    def __generate_next_url(self):
        self.page += 1
        url = self.next_url % (self.page)
        logging.info(url)
        return url

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, headers=self.headers, meta={'spider': 'xueqiu'})

    def parse(self, response):
        if response.status == 400:
            logging.warning("get response failure due to 400")
        elif response.status == 200:
            if response.url == self.root_url:
                pass
            else:
                js = response.body.decode('utf-8')
                comment_obj = JSONDecoder(encoding='utf-8').decode(js)
                for l in comment_obj['list']:
                    item = XueQiuCommentItem()
                    item['id'] = l['id']
                    item['text'] = l['text']
                    item['created_at'] = l['created_at']
                    yield item

                    author_item = XueQiuAuthorItem()
                    author_item['user_id'] = l['user']['id']
                    author_item['screen_name'] = l['user']['screen_name']
                    yield author_item

                    if self.close_down:
                        raise CloseSpider(reason="endpoint reached")
            r = Request(self.__generate_next_url(), dont_filter=True, headers=self.headers, meta={'spider': 'xueqiu'})
            yield r
