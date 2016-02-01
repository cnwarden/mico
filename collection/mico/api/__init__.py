
from elasticsearch import Elasticsearch

class DBAccess(object):

    def __init__(self):
        super(DBAccess, self).__init__()
        self.client = Elasticsearch(hosts=['127.0.0.1:9200'])

    def get_watched_stock(self):
        pass
