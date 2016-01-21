#!/bin/bash

ABS_DIR=`readlink -f $0`
CURRENT_DIR=`dirname $ABS_DIR`
cd $CURRENT_DIR/../command
/usr/local/bin/python start_scrapy.py xueqiu
