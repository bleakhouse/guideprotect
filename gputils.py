# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import logging
import logging.handlers
import platform
import thread
import time
import urllib2
import netifaces as netif
import platform
import redis
from pprint import pprint

import traceback
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO

noisy_logging = None
def show_noisy_logging():
    global noisy_logging
    return  noisy_logging

def set_noisy_logging(noisy):
    global noisy_logging
    if noisy=="noisy_on":
        noisy_logging = 1
    else:
        noisy_logging=None

def make_real_host(url):
    if url is None:
        return
    if url.startswith("http://"):
        url = url[7:]
    if url.startswith("HTTP://"):
        url = url[7:]
    pos  = url.find("/")
    if pos!=-1:
        url = url[:pos]
    return url


def get_redis_obj():

    try:
        redis_obj = redis.Redis()
        return redis_obj
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())


def get_delay_check_redis_obj():

    try:
        redis_obj = redis.Redis(db=2)
        return redis_obj
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


def getIfaceList():
    l = []
    iface={}
    ifacess = netif.interfaces()
    pl = platform.platform()
    ifnames= ifacess

    if pl.startswith("Window"):
        ifnames=[]

        for if1 in ifacess:
            name = get_connection_name_from_guid(if1)


            if len(name)>0:
                iface = {}
                iface['name']=name
                iface['ethname']=if1
                ipv4s = netif.ifaddresses(if1).get(netif.AF_INET, [])
                iface['ip'] = ''
                for entry in ipv4s:
                    iface['ip'] =entry.get('addr')
                    break

                l.append(iface)

    else:
        for if1 in ifacess:
            iface = {}
            iface['name'] = if1
            iface['ethname'] = if1
            ipv4s = netif.ifaddresses(if1).get(netif.AF_INET, [])
            iface['ip']='null'
            for entry in ipv4s:
                iface['ip'] = entry.get('addr')
                break
            l.append(iface)
    return l



def get_connection_name_from_guid(iface_guids):
    import _winreg as wr
    iface_names = ""
    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
    reg_key = wr.OpenKey(reg,
                         r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')

    try:
        reg_subkey = wr.OpenKey(reg_key, iface_guids + r'\Connection')
        iface_names=wr.QueryValueEx(reg_subkey, 'Name')[0]
    except:
        print iface_guids
        pass
    return iface_names



if __name__ =='__main__':

    x= getIfaceList()
    for i in x:
        print i['name']
        print i['ip']


    request_text = '''GET /search?sourceid=chrome&ie=UTF-8&q=ergterst HTTP/1.1\r\nHost: www.google.com\r\nConnection: keep-alive\r\nAccept: application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13\r\nAccept-Encoding: gzip,deflate,sdch\r\nAvail-Dictionary: GeNLY2f-\r\nAccept-Language: en-US,en;q=0.8\r\n'''
    #request_text = '''123123'''
    request = HTTPRequest(request_text)
    try:

        print request.path  # startswith '/', liek '/search?sourceid=chrome&ie=UTF-8&q=ergterst'
        print request.headers['Host']
    except:
        print 'error'
