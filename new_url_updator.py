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
import url_redis_matcher
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

def http_check_url_type(url):

    logging.info('not impl!! '+url)

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

    url_redis_matcher.init_redis()

    while True:

        try:
            if url_redis_matcher.gRedisObj is None:
                raise NameError('redis not init')

            unknow_urls= pop_all_unknow_urls(redis_obj)
            print 'unknow_urls:',len(unknow_urls)
            updating_url_infos={}
            for url in unknow_urls:
                url_info = http_check_url_type(url)
                if url_info is None:
                    continue
                url_type = url_info[0]
                #if url_type != 2:
                #    continue

                urlinfo = {}
                urlinfo['urltype'] = url_type
                urlinfo['evilclass'] = url_info[1]
                urlinfo['redirect_type'] = 'file'
                urlinfo['redirect_target'] = 'safe_navigate.html'
                urlinfo['urlclass'] = url_info[2]
                urlinfo['urlsubclass'] = url_info[3]
                urlinfo['update_time'] = int(time.time())

                updating_url_infos[url]=url_info

            if len(updating_url_infos)>0:
                pip = url_redis_matcher.gRedisObj.pipeline()

                for url,update_info in updating_url_infos:
                    pip.hmset(url.lower(), update_info)

                print 'pip.execute():',pip.execute()

        except:
            pass

        time.sleep(10)


# URL映射
urls = (
    '/', 'Index',
    '/test', 'gptest',
    '/update_url', 'update_url',

)


class update_url:
    def GET(self):

        global  gstart_update
        return "start already ",gstart_update


class Index:
    def GET(self):
        web.header('Content-Type', 'application/html')
        return 'what is this'
    def POST(self):
        return 'what is this post'

class gptest:

    def GET(self):
        try:
            global  redis_obj
            if redis_obj is not None:
                return redis_obj.dbsize(), redis_obj.smembers(gUNKNOW_URL_KEY_NAME)

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
            print "Error: unable to start RuntimEnginThread"


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