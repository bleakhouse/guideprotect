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
import sys
import ConfigParser
import httplib
import basedef
import base64
import gputils
import requests
class HttpQuery(object):
    httpClient = None
    req_host = '127.0.0.1'
    req_port = 8080
    warning_email=[]



    def init_from_cfg(self, cfg):
        cfgobj = ConfigParser.ConfigParser()
        if not os.path.isfile(cfg):
            return

        try:
            cfgobj.read(cfg)
            if cfgobj.has_option('boot', 'url_req_host'):
                self.req_port = cfgobj.getint('boot', 'url_req_port')
            if cfgobj.has_option('boot', 'url_req_host'):
                self.req_host = cfgobj.get('boot', 'url_req_host')

                logging.info('url_req_host:%s', self.req_host)
                logging.info('req_port:%s', self.req_port)
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())




    def init(self):

        try:
            self.init_from_cfg(basedef.GCFG)
            #self.httpClient = httplib.HTTPConnection(self.req_host, self.req_port, timeout=5)
            self.httpClient = requests.Session()
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())

    def http_check_url_type(self,url):

        if url is None:
            return
        if self.httpClient is None:
            return
        try:

            data = None
            httpres=""
            requrl=""
            try:
                if url.startswith('http://') or url.startswith('HTTP://'):
                    url = url[7:]
                encode_url = base64.b64encode(url)
                url = gputils.make_real_host(url)
                requrl = '/API/url_Testing.php?url='+url
                requrl = 'http://'+str(self.req_host)+":"+str(self.req_port)+requrl
                #print requrl
                r = self.httpClient.get(requrl,   headers={'Connection': 'keep-alive'})
                if r.ok is not True:
                    return
                httpres =r.text

                data = json.loads(httpres)
            except Exception, e:
                logging.error(str(e))
                logging.error(traceback.format_exc())
                if basedef.GWARNING:basedef.GWARNING.sendmail(str(e), traceback.format_exc())
                print httpres[:100]
                logging.info('req url:%s', requrl)
                logging.info(' url:%s', url)
                #self.httpClient = httplib.HTTPConnection(self.req_host, self.req_port, timeout=5)
                self.httpClient = requests.Session()
                return 1
            if not data.has_key("status"):
                return

            if data['status']==100:
                logging.warning('repeat url req: %s', url)
                return
            # if data['status']!=0:
            #     logging.warning('error req url %s,%s', str(data), url)
            #     return

            hasfalse = False
            r=[]
            if not data.has_key('url_attr'):
                logging.warning('has no url attr %s', str(data))
                return

            url_attr=data['url_attr']
            keys = ["urltype","eviltype","evilclass","urlclass","urlsubclass",]
            for k in keys:
                if not url_attr.has_key(k):
                    hasfalse=True
                    break
                r.append(str(url_attr[k]))
            if hasfalse:
                return
            return r

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
# obj = HttpQuery()
# obj.init()
# fp =open('''''')
# for line in fp:
#     line = line.lower()
#     pos = line.find("/",7)
#     if pos!=-1:
#         line = line[:pos]
#     obj.http_check_url_type(line)

