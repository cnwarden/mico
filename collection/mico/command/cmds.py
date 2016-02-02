

import getopt
from mico.util.esagent import ESAgent
from mico.settings import ES_HOST, ES_INDEX, ES_REF_INDEX, ES_TIMESERIES_INDEX, ES_CONFIG_INDEX
import sys


if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], 'cia:r:l', ['clean', 'init', 'addwatch', 'removewatch', 'listwatch'])

    settings = {}
    settings['ES_HOST'] = ES_HOST
    settings['ES_INDEX'] = ES_INDEX
    settings['ES_REF_INDEX'] = ES_REF_INDEX
    settings['ES_TIMESERIES_INDEX'] = ES_TIMESERIES_INDEX
    settings['ES_CONFIG_INDEX'] = ES_CONFIG_INDEX

    for o, a in opts:
        if o == '-c':
            agent = ESAgent(settings = settings)
            agent.clean()
            print 'clean up elasticsearch'
        elif o == '-i':
            agent = ESAgent(settings = settings)
            agent.clean()
            agent.initalize()
            print 'reinitalize the elasticsearch'
        elif o == '-a':
            print 'add symbol:%s' % (a)
            agent = ESAgent(settings = settings)
            agent.add_symbol_to_watch(a)
        elif o == '-r':
            print 'remove symbol:%s' % (a)
            agent = ESAgent(settings = settings)
            agent.remove_symbol_to_watch(a)
        elif o == '-l':
            print 'list symbol'
            agent = ESAgent(settings = settings)
            print agent.get_watched_symbol()
