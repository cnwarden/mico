
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random


class RotateUserAgent(UserAgentMiddleware):
    """
        Rotate User Agent provides changing user-agent to avoid crawl
        user agent: http://www.useragentstring.com/pages/useragentstring.php
    """

    user_agent_list = [
        'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'
    ]

    def __init__(self, user_agent='mico'):
        super(RotateUserAgent, self).__init__(user_agent)

    def process_request(self, request, spider):
        ua = ''
        if hasattr(spider, 'user_agent'):
            ua = spider.user_agent
        else:
            ua = random.choice(self.user_agent_list)

        request.headers.setdefault('USER-AGENT', ua)
