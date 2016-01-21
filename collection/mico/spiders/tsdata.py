# -*- coding:utf-8 -*-
# http://quotes.money.163.com/service/chddata.html?
# code=0000001&start=19901219&end=20160120&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER


from scrapy.spiders.crawl import Spider
from scrapy.exceptions import CloseSpider
from scrapy.http import Request
from mico.items import *
import re
from datetime import datetime
import time


class TimeSeriesSpider(Spider):

    name = 'timeseries'
    headers = {
            'ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,ja;q=0.2,zh-TW;q=0.2'
        }

    def __init__(self, **kwargs):
        super(TimeSeriesSpider, self).__init__(name=self.name, **kwargs)
        self.close_down = False
        self.start_urls = ['http://quotes.money.163.com/service/chddata.html?\
        code=0000001&start=19901219&end=20160120&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;VOTURNOVER;VATURNOVER']

    def make_requests_from_url(self, url):
        return Request(url, method='GET', headers=self.headers)

    def parse(self, response):
        if response.status == 200:
            for line in response.body.split('\n'):
                if self.close_down:
                    raise CloseSpider(reason='reach the limit')
                if re.search('^\d{4}-\d{2}-\d{2}', line):
                    ds = line.split(',')
                    item = TimeSeriesItem()
                    dt = datetime.strptime(ds[0], '%Y-%m-%d')
                    item['time'] = time.mktime(dt.timetuple())
                    item['code'] = ds[1][1:]
                    item['closeprc'] = float(ds[3])
                    item['highprc'] = float(ds[4])
                    item['lowprc'] = float(ds[5])
                    item['openprc'] = float(ds[6])
                    yield item
            yield TimeSeriesAdminEndItem()
