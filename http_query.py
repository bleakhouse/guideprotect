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

class HttpQuery(object):
    httpClient = None
    req_host = '127.0.0.1'
    req_port = 8080


    def init_from_cfg(self, cfg):
        cfgobj = ConfigParser.ConfigParser()
        if not os.path.isfile(cfg):
            return

        try:
            cfgobj.read()
            if not cfgobj.has_option('boot', 'url_req_host'):
                return
            self.url_req_port = cfgobj.getint('boot', 'url_req_port')

            logging.info('url_req_host:%s', self.url_req_host)
            logging.info('url_req_host:%s', self.req_port)

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())


    def init(self):

        try:
            self.httpClient = httplib.HTTPConnection(self.req_host, self.req_port, timeout=5)
            self.init_from_cfg(basedef.GCFG)

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())

    def http_check_url_type(self,url):

        if url is None:
            return
        if self.httpClient is None:
            return
        try:

            if url.startswith('http://'):
                url = url[7:]

            self.httpClient.request('GET', '/j2ee002/{0}.do'.format(url))

            # response是HTTPResponse对象
            response = self.httpClient.getresponse()
            data = json.loads( response.read())
            hasfalse = False
            r=[]
            keys = ["urltype","eviltype","evilclass","urlclass","urlsubclass",]
            for k in keys:
                if not data.has_keys(k):
                    hasfalse=True
                    break
                r.append(data[k])
            if hasfalse:
                return
            return r

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
