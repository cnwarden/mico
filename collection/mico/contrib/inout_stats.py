

from scrapy.downloadermiddlewares.stats import DownloaderStats


class InOutStats(DownloaderStats):

    def __init__(self, stats):
        super(InOutStats, self).__init__(stats)

    def process_request(self, request, spider):
        pass

    def process_response(self, request, response, spider):
        self.stats.inc_value('total/total_items', spider=spider)
        return response
