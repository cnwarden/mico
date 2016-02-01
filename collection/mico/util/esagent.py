

from elasticsearch import Elasticsearch

class ESAgent(object):

    def __init__(self, *args, **kwargs):
        self.agent = Elasticsearch(hosts=kwargs['hosts'])

        self.INDEX_XUEQIU='xueqiu_t'
        self.indices = [self.INDEX_XUEQIU, 'reference_t', 'timeseries_t']

    def initalize(self):
        for index in self.indices:
            body = ''
            if index == self.INDEX_XUEQIU:
                body = {
                    'mappings':{
                      'comment':{
                          'properties':{
                              'content':{
                                    'type':'nested',
                                    'properties':{
                                        'symbol': { 'type':'string', 'index':'not_analyzed' }
                                    }
                              }
                          }
                      }
                    },
                    'aliases':{'all_xueqiu':{}}
                }
            self.agent.indices.create(index,
                                      body=body,
                                      ignore=400) #ignore indices exists

    def clean(self):
        for index in self.indices:
            self.agent.indices.delete(index=index, ignore=(400, 404))

    def exist_indices(self, index):
        return self.agent.indices.exists(index=index)

    # XueQiu Comment API
    def get_last_comment_id(self, symbol):
        doc = self.agent.search(index=self.INDEX_XUEQIU,
                          doc_type='comment',
                          body={
                              'size': 1,
                              'query': {
                                  'match':
                                      { 'comment.symbol': symbol }
                              },
                              'sort': [
                                  {'comment.id': {'order': 'desc'}}
                              ]
                          },
                          ignore=(400, 404))
        if not doc.has_key('status'):
            return doc['hits']['hits'][0]['_source']['comment']['id']
        else:
            return 0

    def create_comment(self, doc):
        self.agent.create(index=self.INDEX_XUEQIU, doc_type="comment", id=doc['content']['id'], body=doc, ignore=(409))
