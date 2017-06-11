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

#1 blocked
#2 safe
#3 unknow
#4 check,but unknow


# 0-1 未知 访问暂无风险 正常访问
# 2 风险网址 访问有安全风险 阻断或提醒
# 3-4 安全 访问无风险 正常访问

def is_blocked_url(url_or_host):

    if url_or_host is None:
        return [3]

    val = gRedisObj.hmget(url_or_host, ['urltype','evilclass','redirect_type', 'redirect_target', 'update_time'])

    if val is None or val[0] is None:
        return [3]

    if basedef.GP_URL_TYPE_VALID_TIMES!=-1:
        update_time = val[4]
        if update_time is not None and time.time()-int(update_time)>basedef.GP_URL_TYPE_VALID_TIMES:
            return [3]

    urltype = val[0]
    if urltype is None or not urltype.isdigit():
        return [3]

    if urltype in ["0", "1"]:
        return [4]

    if urltype in [2]:
        return [1]+val

    if urltype in ["3", "4"]:
        return [2]

    return [3]

def make_redirect_info(val):

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

def get_direct_info( host,req, short_host=None):
    global gRedisObj
    if gRedisObj is None:
        return

    if should_pass_by_shothost(short_host)==True:
        return

    newval = is_blocked_url(host)

    if newval[0]==2:
        return

    if newval[0]==3:
        new_unknow_url(host)

    if newval[0]==1:
        return make_redirect_info(newval[1:])

    fullurl = host + req
    newval = is_blocked_url(fullurl)

    if newval[0]==1:
        return make_redirect_info(newval[1:])

    if newval[0]==3:
        new_unknow_url(fullurl)

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


