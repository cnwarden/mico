# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from mico.util.toolbox import TimeHelper, TimeService


class XueQiuCommentItem(scrapy.Item):
    """
    created_at in Epoch Time(UTC)
    """
    id = scrapy.Field()
    text = scrapy.Field()
    created_at = scrapy.Field() # in Epoch Time(UTC)
    symbol = scrapy.Field()
    ticker = scrapy.Field()

    def toJson(self):
        ts = TimeService(self.get('created_at')/1000)
        return {
            'content':
                {
                    'id': self.get('id'),
                    'text': self.get('text'),
                    'created_at': self.get('created_at'),
                    'created_at_str': ts.get_local_time().strftime("%Y-%m-%d %H:%M:%S"),
                    'symbol': self.get('symbol'),
                    'ticker': self.get('ticker')
                }
        }

class XueQiuAuthorItem(scrapy.Item):
    user_id = scrapy.Field()
    screen_name = scrapy.Field()

    def toJson(self):
        """
        this is a update query, set root to 'doc'
        :return:
        """
        return {
            'doc':{
                'author':{
                    'uid': self.get('user_id'),
                    'name': self.get('screen_name')
                }
            }
        }


class ReferenceItem(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()

    def toJson(self):
        return {
                'code': self.get('code')[1:]+'.SH',
                'name': self.get('name')
        }


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
