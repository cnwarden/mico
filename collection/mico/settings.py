# -*- coding: utf-8 -*-

# Scrapy settings for stock_news project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'mico_bot'

SPIDER_MODULES = ['mico.spiders']
NEWSPIDER_MODULE = 'mico.spiders'

LOG_ENABLED = True
LOG_LEVEL = 'INFO'
#LOG_FILE = 'mico.log'
#LOG_STDOUT = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'stock_news (+http://www.yourdomain.com)'
#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:43.0) Gecko/20100101 Firefox/43.0'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
#COOKIES_ENABLED=False
COOKIES_ENABLED=True
COOKIES_DEBUG=True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'stock_news.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'mico.contrib.rotate_useragent.RotateUserAgent': 300,
    'mico.contrib.inout_stats.InOutStats':200,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'mico.pipelines.XueQiuCommentPipeline': 300,
    'mico.pipelines.XueQiuAuthorPipeline': 400,
}

REFERENCE_ITEM_PIPELINES = {
    'mico.pipelines.ReferencePipeline': 300,
}

TIMESERIES_ITEM_PIPELINES = {
    'mico.pipelines.TimeSeriesPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'


# ElasticSearch
ES_HOST=[{'host':'127.0.0.1','port':9200}]
ES_INDEX='xueqiu'
ES_REF_INDEX='reference'
ES_TIMESERIES_INDEX='timeseries'

#from elasticsearch import Elasticsearch
#es_client = Elasticsearch(ES_HOST)
#es_client#.indices.delete(index=ES_INDEX,ignore=(400,404))
import logging
tracer = logging.getLogger('elasticsearch.trace')
tracer.setLevel(logging.INFO)
tracer.addHandler(logging.NullHandler())
