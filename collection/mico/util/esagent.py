

from elasticsearch import Elasticsearch

class ESAgent(object):
    """
    ESAgent warpper class for ES operation
    """
    def __init__(self, *args, **kwargs):
        """
        init from settings key/value of ES
        :param args:
        :param kwargs:
        :return:
        """
        settings = kwargs['settings']
        self.agent = Elasticsearch(hosts=settings['ES_HOST'])

        for key in settings:
            if key.upper().startswith('ES_'):
                self.__setattr__(key.upper(), settings[key])

        self.indices = [self.ES_INDEX, self.ES_REF_INDEX, self.ES_TIMESERIES_INDEX, self.ES_CONFIG_INDEX]

    def initalize(self):
        for index in self.indices:
            body = ''
            if index == self.ES_INDEX:
                body = {
                    'mappings':{
                      'comment':{
                          'properties':{
                              'content':{
                                    # object
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

    def add_user(self, uid):
        pass

    def remove_user(self, uid):
        pass

    def get_watched_symbol(self):
        doc = self.agent.search(index=self.ES_CONFIG_INDEX,
                                doc_type='watch_symbols',
                                body={
                                    'size': 100,
                                    'query':{
                                        'match_all': {}
                                    },
                                    'sort':[
                                        {
                                            'symbol':{'order': 'asc'}
                                        }
                                    ]
                                })
        if not doc.has_key('status') and doc['hits']['total'] > 0:
            return [item['_source']['symbol'] for item in doc['hits']['hits']]
        else:
            return []

    def add_symbol_to_watch(self, symbol):
        self.agent.create(index=self.ES_CONFIG_INDEX,
                          doc_type="watch_symbols",
                          id=symbol,
                          body={
                              'symbol':symbol
                          },
                          ignore=(409))

    def remove_symbol_to_watch(self, symbol):
        self.agent.delete(index=self.ES_CONFIG_INDEX,
                          doc_type='watch_symbols',
                          id=symbol,
                          ignore=(404))

    # XueQiu Comment API
    def get_last_comment_id(self, symbol):
        doc = self.agent.search(index=self.ES_INDEX,
                          doc_type='comment',
                          body={
                              'size': 1,
                              'query': {
                                  'match':
                                      { 'content.symbol': symbol }  # not_analyzed this field like term
                              },
                              'sort': [
                                  {'content.id': {'order': 'desc'}}
                              ]
                          },
                          ignore=(400, 404))
        if not doc.has_key('status') and doc['hits']['total'] > 0:
            return doc['hits']['hits'][0]['_source']['content']['id']
        else:
            return 0

    def create_comment(self, doc):
        self.agent.create(index=self.ES_INDEX, doc_type="comment", id=doc['content']['id'], body=doc, ignore=(409))


    def update_comment_with_author(self, id, body):
        self.agent.update(index=self.ES_INDEX, doc_type='comment', id=id, body=body, ignore=(400))


    def create_reference(self, doc):
        self.agent.create(index=self.ES_REF_INDEX, doc_type='instrument', id=doc['code'], body=doc, ignore=(400))

