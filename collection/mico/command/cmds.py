

import getopt
from mico.util.esagent import ESAgent
import sys


if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], 'ci', ['clean', 'init'])

    for o, a in opts:
        if o == '-c':
            agent = ESAgent(hosts=['127.0.0.1:9200'])
            agent.clean()
            print 'clean up elasticsearch'
        elif o == '-i':
            agent = ESAgent(hosts=['127.0.0.1:9200'])
            agent.clean()
            agent.initalize()
            print 'reinitalize the elasticsearch'
