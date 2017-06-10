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
import new_url_updator

gRedisObj=None
gTargetFile={}
gRedisObj_unknow=None


def new_unknow_url(url):
    global  gRedisObj_unknow
    if gRedisObj_unknow is None:
        return
    gRedisObj_unknow.sadd(new_url_updator.gUNKNOW_URL_KEY_NAME, url)

def should_pass_by_shothost(short_host):
    if short_host is not None:
        val2 = gRedisObj.hmget(short_host, ['urltype','evilclass','redirect_type', 'redirect_target', 'update_time'])
        if val2 is None or val2[0] is None:
            new_unknow_url(short_host)
        else:
            urltype = val2[0]
            if urltype is None or not urltype.isdigit():
                return
            if int(urltype) == 3 or int(urltype) == 4:  # 2 means risky url
                return True

def get_direct_info( host,req, short_host=None):
    global gRedisObj
    if gRedisObj is None:
        return

    fullurl =host+req

    if should_pass_by_shothost(short_host)==True:
        return

    if should_pass_by_shothost(host)==True:
        return

    val = gRedisObj.hmget(fullurl, ['urltype','evilclass','redirect_type', 'redirect_target', 'update_time'])

    if val is None or val[0] is None:
        new_unknow_url(fullurl)
        return

    if basedef.GP_URL_TYPE_VALID_TIMES!=-1:
        update_time = val[4]
        if update_time is not None and time.time()-int(update_time)>basedef.GP_URL_TYPE_VALID_TIMES:
            new_unknow_url(fullurl) # over time,need to check timer again
            return

    urltype = val[0]
    if urltype is None or not urltype.isdigit():
        return

    if int(urltype) != 2: # 2 means risky url
        return

    redirect_type = val[2]
    redirect_target=val[3]

    if redirect_type is None or redirect_target is None:
        return

    if redirect_type == RULE_ATTR_NAME_redirect_type_url or redirect_type == RULE_ATTR_NAME_redirect_type_buf :
        return [redirect_type, redirect_target]

    if redirect_type != RULE_ATTR_NAME_redirect_type_file:
        return

    if redirect_target in gTargetFile.keys():
        return [RULE_ATTR_NAME_redirect_type_buf, gTargetFile[redirect_target]]

    try:
        if os.path.isfile(redirect_target):
            gTargetFile[redirect_target] = open(redirect_target, 'r').read()
        return [RULE_ATTR_NAME_redirect_type_buf, gTargetFile[redirect_target]]
    except:
        pass

    return

def init_redis(host='127.0.0.1', port=6379):

    try:
        global gRedisObj
        gRedisObj = redis.Redis(host=host, port=port)
        print 'url size:',gRedisObj.dbsize()
        global gRedisObj_unknow
        gRedisObj_unknow = new_url_updator.get_unknow_redis_db()
        print 'unknow url size:', gRedisObj_unknow.dbsize()

    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
def save_data():
    global gRedisObj
    if gRedisObj is None:
        return

    gRedisObj.save()


if __name__=='__main__':
    init_redis()


