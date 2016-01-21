# -*- coding:utf-8 -*-

from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
from json import JSONDecoder
from mico.items import *

class ReferenceSpider(Spider):
    """
        163 reference list:
        http://quotes.money.163.com/hs/service/marketradar_ajax.php?page=50&query=STYPE:EQA;EXCHANGE:CNSESH&count=100&type=query&order=desc

        http://quotes.money.163.com/hs/service/diyrank.php?page=0&query=STYPE:EQA;EXCHANGE:CNSESH&sort=SYMBOL&order=asc&count=100&type=query
    """
    name = 'reference'

    #base_url = 'http://quotes.money.163.com/hs/service/marketradar_ajax.php?page=%d&query=%s&count=%d&type=query&order=desc'
    base_url = 'http://quotes.money.163.com/hs/service/diyrank.php?page=%d&query=%s&sort=SYMBOL&order=asc&count=%d&type=query'
    page = 0

    section = 'STYPE:EQA;EXCHANGE:CNSESH'
    page_count = 500

    headers = {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,ja;q=0.2,zh-TW;q=0.2'
        }

    def __init__(self, **kwargs):
        super(ReferenceSpider, self).__init__(name='reference', **kwargs)
        self.start_urls.append(self.__generate_next_url())

    def __generate_next_url(self):
        url = self.base_url % (self.page, self.section, self.page_count)
        self.page += 1
        return url

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, headers=self.headers)

    def parse(self, response):
        if response.status == 200:
            jsobj = JSONDecoder(encoding='utf-8').decode(response.body.decode('utf-8'))
            if len(jsobj['list']) == 0:
                raise CloseSpider(reason='no more pages')
            else:
                for instrument in jsobj['list']:
                    item = ReferenceItem()
                    item['code'] = instrument['CODE']
                    item['name'] = instrument['SNAME']
                    yield item
        r = Request(self.__generate_next_url())
        yield r

