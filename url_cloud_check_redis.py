# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging
import basedef
import redis
import traceback
from basedef import *
import os
import MySQLdb
import datetime
import gpwarning
import http_query
import gputils

class url_cloud_checker(object):

    sip=0
    sport=0
    redobj=None
    url_checker_pub_channel=''
    redis_match_obj=None
    def init(self):
        cfgobj = basedef.GCS.get_config_obj()
        url_checker_pub_redis_num = cfgobj.getint('boot','url_checker_pub_redis_num')
        self.url_checker_pub_channel = cfgobj.get('boot','url_checker_pub_channel')
        self.redobj = redis.Redis(db=url_checker_pub_redis_num)
        logging.info('url_checker_pub_redis_num:%s,%s', url_checker_pub_redis_num, self.redobj)
        logging.info('url_checker_pub_channel:%s', self.url_checker_pub_channel)

        queryobj = http_query.HttpQuery()
        queryobj.init()
        redis_match_obj = gputils.get_redis_obj()

    def add_new_unknown_url(self, url, isvisiting=True):

        dat = {'_dtype':3, 'url':url, 'isvisiting':isvisiting}
        self.save2pub(dat)

    def save2pub(self, data):
        if self.redobj==None:
            logging.error('self.redobj error:%s',data)
        self.redobj.publish('self.url_checker_pub_channel', (data))

    def new_url_handler(self):

        number=0
        for item in self.ps.listen():
            if item['type']!='message':
                continue
            number = number+1
            msg = item['data']
            data = eval(msg)


#         NOT USING      !!!!!!!!!!!!!!!!!!!!!!!!!!!!
#considering performance, should not write evey single record everytime.

