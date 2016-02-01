

import unittest
import time
from mico.util.esagent import *
from mico.util.toolbox import *

class agentTest(unittest.TestCase):

    def setUp(self):
        self.agent = ESAgent(hosts=['127.0.0.1:9200'])

    def testCreate(self):
        self.agent.initalize()
        self.assertEquals(self.agent.exist_indices('xueqiu'), True)

    def testCleanup(self):
        pass
        self.agent.clean()
        self.assertEquals(self.agent.exist_indices('xueqiu'), False)


class toolboxTest(unittest.TestCase):

    def testGetLocalTime(self):
        ts = TimeService(1454160474)
        print ts.get_epoch_time()
        print ts.get_local_time()
        print ts.get_utc_time()

    def testGetMidnightEpoch(self):
        print '---------------'
        print TimeHelper.get_today_epoch_time()

class MyTest(unittest.TestCase):

    def testArrary(self):
        t = [1,2,3]
        print t.pop()
        print t.pop()
        print t.pop()


if __name__ == '__main__':
    pass
