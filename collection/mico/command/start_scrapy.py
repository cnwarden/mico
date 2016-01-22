#!/usr/bin/env python

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from twisted.internet import reactor
import sys


def run_spider(args):
    settings = get_project_settings()

    name = args[0]
    paras = dict(x.split('=', 1) for x in args[1:])

    if name == 'reference':
        settings.set('ITEM_PIPELINES', settings['REFERENCE_ITEM_PIPELINES'])
    elif name == 'timeseries':
        settings.set('ITEM_PIPELINES', settings['TIMESERIES_ITEM_PIPELINES'])

    process = CrawlerProcess(settings)
    process.crawl(name, **paras)
    process.start()


def run_loop():
    print('heartbeat!--->%s' % (datetime.now().strftime("%d/%m/%y %H:%M:%S")))

if __name__ == "__main__":
    spider = None
    if len(sys.argv) > 0:
        run_spider(sys.argv[1:])
