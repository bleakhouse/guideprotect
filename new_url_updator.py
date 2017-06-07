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

redis_obj =None

gUNKNOW_URL_KEY_NAME = 'guide:protect:unknow_urls'

def get_redis(host='127.0.0.1', port=6379,db=1):

    try:
        redis_obj = redis.Redis(host=host, port=port)
        return redis_obj
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())

def http_check_url_type(url):

    print 'not impl!!'

def do_update(name):

    global  redis_obj
    redis_obj = get_redis()

    if redis_obj is None:
        return

    while True:

        try:
            if url_redis_matcher.gRedisObj is None:
                raise NameError('redis not init')

            pip = redis_obj.pipeline()
            unknow_urls = pip.smembers(gUNKNOW_URL_KEY_NAME)
            pip.flushdb()
            pip.execute()

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
        if url_redis_matcher.gRedisObj is None:
            url_redis_matcher.init_redis()



# URL映射
urls = (
    '/', 'Index',
    '/test', 'gptest',

)

class Index:
    def GET(self):
        web.header('Content-Type', 'application/json')
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
    def Start(self):
        try:
            thread.start_new_thread(do_update, ("do_update-1",))
        except:
            print "Error: unable to start RuntimEnginThread"


import ConfigParser
if __name__=='__main__':

    reload(sys).setdefaultencoding("utf8")
    print 'system encoding: ',sys.getdefaultencoding()

    run_url_updator().Start()
    app = web.application(urls, globals())
    app.notfound = notfound
    app.run()