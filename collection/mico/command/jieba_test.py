# -*- coding:utf-8 -*-

import logging
import sys
import jieba

jieba.default_logger.handlers = []

logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger("jieba_test")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

jieba.load_userdict('../dict/stock.dict')


def cut(text):
    seg_list = jieba.cut(text, cut_all=False)
    logger.debug('/ '.join(seg_list))

cut('由此带来的市场空间将达万亿规模，辉丰股份')
cut('雪球这两天言论数极剧下降，大家都不谈票票了，是入场的时机到了吗？')
cut('海南高速  参股公司IPO获证监会正式核准南京医药  比上年同期增长')
