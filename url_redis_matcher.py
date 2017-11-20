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
import gputils
gRedisObj=None

gTargetFile={}
gRedisObj_unknow=None

def make_real_host(url):
    return gputils.make_real_host(url)

def new_unknow_url(url):
    global  gRedisObj_unknow
    if gRedisObj_unknow is None:
        return
    url_info={}
    url_info['url']=url
    url_info['need_save_log_redis']=0
    gRedisObj_unknow.rpush(new_url_updator.gUNKNOW_URL_KEY_NAME, (url_info))

def add_unknow_url_info(url_info):
    global  gRedisObj_unknow
    if gRedisObj_unknow is None:
        return
    gRedisObj_unknow.rpush(new_url_updator.gUNKNOW_URL_KEY_NAME, (url_info))

def should_pass_by_shothost(short_host, dicret):
    if short_host is not None:
        val2 = gRedisObj.hmget(short_host, ['urltype','evilclass','redirect_type', 'redirect_target', 'update_time', 'urlclass'])

        if val2 is None or val2[0] is None:
            new_unknow_url(short_host)
        else:
            dicret.append(val2[0])
            dicret.append(val2[1])
            dicret.append(val2[5])
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

def is_blocked_url(url_or_host, dicret):

    if url_or_host is None:
        return [3]
    url_or_host = make_real_host(url_or_host)
    val = gRedisObj.hmget(url_or_host, ['urltype','evilclass','redirect_type', 'redirect_target', 'update_time', 'urlclass'])


    if val is None or val[0] is None:
        return [3]
    dicret.append(val[0])
    dicret.append(val[1])
    dicret.append(val[5])

    if basedef.GP_URL_TYPE_VALID_TIMES!=-1:
        update_time = val[4]
        if update_time is not None and time.time()-int(update_time)>basedef.GP_URL_TYPE_VALID_TIMES:
            return [3]

    urltype = val[0]
    if urltype is None or not urltype.isdigit():
        return [3]

    if urltype in ["0", "1"]:
        update_time = val[4]
        if update_time is not None and time.time()-int(update_time)>3600*24*2: #
            new_unknow_url(url_or_host) #over 2days .we should check it again!!
        return [4] #check,but unknow

    if urltype in ["2"]:
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

def get_direct_info( host,req, useragent, referer, short_host=None):

    url_info=[]
    if should_pass_by_shothost(short_host,url_info)==True:
        if len(url_info)>0 and basedef.GSaveLogRedisPub:
            basedef.GSaveLogRedisPub.save_url_info(host + req, url_info[0], url_info[1], url_info[2],
                                                   referer, useragent)
        return

    url_info = []
    newval = is_blocked_url(host,url_info)
    if newval[0]==2:
        if len(url_info) > 0 and basedef.GSaveLogRedisPub:
            basedef.GSaveLogRedisPub.save_url_info(host + req, url_info[0], url_info[1], url_info[2],
                                                   referer, useragent)
        return

    if newval[0]==3:
        new_unknow_url(make_real_host(host))

    if newval[0]==1:
        if len(url_info) > 0 and basedef.GSaveLogRedisPub:
            basedef.GSaveLogRedisPub.save_url_info(host + req, url_info[0], url_info[1], url_info[2],
                                                   referer, useragent)
        return make_redirect_info(newval[1:])

    fullurl = host + req
    url_info = []
    newval = is_blocked_url(fullurl,url_info)
    if len(url_info) > 0 and basedef.GSaveLogRedisPub:
        basedef.GSaveLogRedisPub.save_url_info(fullurl, url_info[0], url_info[1], url_info[2],referer, useragent)
    if newval[0]==1:
        return make_redirect_info(newval[1:])

    if newval[0]==3:
        visit_time = time.strftime('%Y-%m-%d %H:%M:%S')

        checking_url_info={}
        checking_url_info['url'] = fullurl
        checking_url_info['need_save_log_redis'] = 1
        checking_url_info['useragent'] = useragent
        checking_url_info['sip'] = basedef.GSaveLogRedisPub.sip
        checking_url_info['sport'] = basedef.GSaveLogRedisPub.sport
        checking_url_info['visit_time'] = visit_time
        checking_url_info['referer'] = referer
        add_unknow_url_info(checking_url_info)

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


