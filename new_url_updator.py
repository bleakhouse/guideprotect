# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import logging
import logging.handlers
import platform
import thread
import time
import re
import os
import redis
import traceback
import web
import sys
import http_query

import datetime

redis_obj =None
gstart_update = 0

gUNKNOW_URL_KEY_NAME = 'guide:protect:unknow_urls'

def get_unknow_redis_db(host='127.0.0.1', port=6379,db=1):

    try:
        redis_obj = redis.Redis(host=host, port=port, db=db)
        return redis_obj
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())



def get_redis_obj():

    try:
        redis_obj = redis.Redis()
        return redis_obj
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())

def pop_all_unknow_urls(redis_obj):

    unknow_urls = redis_obj.smembers(gUNKNOW_URL_KEY_NAME)
    redis_obj.flushdb()
    return unknow_urls

def do_update(name):

    global  gstart_update
    timeNow = datetime.datetime.now()
    gstart_update = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    gstart_update = name + " " + gstart_update
    global  redis_obj
    redis_obj = get_unknow_redis_db()

    if redis_obj is None:
        return

    redis_match_obj = get_redis_obj()
    redis_match_obj.set('update_info', gstart_update)

    queryobj = http_query.HttpQuery()
    queryobj.init()

    while True:

        try:
            if redis_match_obj is None:
                raise NameError('redis not init')

            unknow_urls= pop_all_unknow_urls(redis_obj)
            count = len(unknow_urls)
            if count>0:
                logging.info('unknow urls:%s', len(unknow_urls))
            updating_url_infos={}
            for url in unknow_urls:
                url_info = queryobj.http_check_url_type(url)
                if url_info is None:
                    continue
                url_type = url_info[0]
                #if url_type != 2:
                #    continue

                urlinfo = {}
                urlinfo['urltype'] = url_type
                urlinfo['eviltype'] = url_info[1]
                urlinfo['evilclass'] = url_info[2]
                urlinfo['redirect_type'] = 'file'
                urlinfo['redirect_target'] = 'safe_navigate.html'
                urlinfo['urlclass'] = url_info[3]
                urlinfo['urlsubclass'] = url_info[4]
                urlinfo['update_time'] = int(time.time())
                urlinfo['info_src'] = 'tx_online_query'

                if urlinfo['redirect_type']=='url':
                    if len(urlinfo['redirect_target'])>0 and not urlinfo['redirect_target'].startswith('http://'):
                        urlinfo['redirect_target'] ='http://'+urlinfo['redirect_target']

                updating_url_infos[url]=url_info

            if len(updating_url_infos)>0:
                pip = redis_match_obj.pipeline()

                for url,update_info in updating_url_infos:
                    pip.hmset(url.lower(), update_info)

                logging.info('pip.execute():%s',pip.execute())

        except:
            pass

        time.sleep(10)

    redis_match_obj.delete('update_info', gstart_update)

# URL映射
urls = (
    '/', 'Index',
    '/test', 'gptest',
    '/update_url', 'update_url',
    '/get_url', 'get_url',

)
class get_url:
    def GET(self):
        obj = get_redis_obj()
        if obj is None:
            return 'conn fail'
        url =web.input().get('url')
        if url is None or len(url)==0:
            return 'error pars'
        url = url.lower()
        info = obj.hgetall(url)
        return info


class update_url:
    def GET(self):
        return "start already ",get_redis_obj().get('update_info')


class Index:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return 'what is this'
    def POST(self):
        return 'what is this post'

class gptest:

    def GET(self):
        try:
            redis_obj = get_redis_obj()
            if redis_obj is not None:
                return redis_obj.dbsize()

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())

                        #定义404错误显示内容
def notfound():

    return web.notfound("Sorry, the page you were looking for was not found^_^")

class run_url_updator(object):
    def Start(self, name='do_update-1'):
        try:
            thread.start_new_thread(do_update, (name,))
        except:
            print "Error: unable to start run_url_updator"



import ConfigParser
import mylogging
if __name__=='__main__':

    mylogging.setuplog('url_updator.txt')
    reload(sys).setdefaultencoding("utf8")
    print 'system encoding: ',sys.getdefaultencoding()

    run_url_updator().Start()
    app = web.application(urls, globals())
    app.notfound = notfound
    app.run()