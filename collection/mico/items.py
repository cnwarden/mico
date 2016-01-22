# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class XueQiuAuthorItem(scrapy.Item):
    user_id = scrapy.Field()
    screen_name = scrapy.Field()


class XueQiuCommentItem(scrapy.Item):
    id = scrapy.Field()
    text = scrapy.Field()
    created_at = scrapy.Field()


class ReferenceItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()


class TimeSeriesItem(scrapy.Item):
    time = scrapy.Field()
    code = scrapy.Field()
    highprc = scrapy.Field()
    lowprc = scrapy.Field()
    openprc = scrapy.Field()
    closeprc = scrapy.Field()


class TimeSeriesAdminStartItem(scrapy.Item):
    code = scrapy.Field()


class TimeSeriesAdminEndItem(scrapy.Item):
    end = scrapy.Field()
