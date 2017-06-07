# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging
import basedef
import redis
import traceback

gRedisObj=None

def get_direct_info(self, host,req):
    global gRedisObj
    if gRedisObj is None:
        return


def init_redis(host='127.0.0.1', port=6379):

    try:
        global gRedisObj
        gRedisObj = redis.Redis(host=host, port=port)
        print gRedisObj.dbsize()
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())

if __name__=='__main__':
    init_redis()


