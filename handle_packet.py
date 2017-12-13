# -*- coding: UTF-8 -*-
__author__ = 'Administrator'

from scapy.all import *

import basedef
import gputils
import url_redis_matcher
import redis
import logging




class publisher(object):
    redobj=None
    save_log_pub_channel=''
    redis_snapshot=None
    save_log_pub_fullurl_detail = ''
    is_filter=True

    def do_filter(self, do):
        self.is_filter=do

    def init(self):
        save_log_pub_redis_num=0
        cfgobj = basedef.GCS.get_config_obj()
        save_log_pub_redis_num = cfgobj.getint('boot', 'save_log_pub_redis_num')
        self.save_log_pub_channel = cfgobj.get('boot', 'save_log_pub_channel')

        self.redobj = redis.Redis(db=save_log_pub_redis_num)

        save_log_fullurl_detail_redis_num = cfgobj.getint('boot', 'save_log_fullurl_detail_redis_num')
        self.save_log_pub_fullurl_detail = cfgobj.get('boot', 'save_log_fullurl_detail_key')

        self.redis_snapshot = redis.Redis(db=save_log_fullurl_detail_redis_num)

        logging.info('save_log_pub_redis_num:%s,%s', save_log_pub_redis_num, self.redobj)
        logging.info('save_log_pub_channel:%s', self.save_log_pub_channel)


    def save5element(self, sip,sport,prot, dip, dport):

        visit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        dat = {'_dtype':1, 'sip':sip, 'sport':sport,'prot':prot, 'dip':dip, 'dport':dport,'visit_time':visit_time}
        self.save2pub(dat)

    def save_url_info(self, sip,sport,fullurl, urltype, evilclass, urlclass,referer, useragent='unknow'):
        visit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        dat = {'_dtype':2, 'sip':sip, 'sport':sport,'fullurl':fullurl, 'urltype':urltype, 'evilclass':evilclass, 'urlclass':urlclass, 'useragent':useragent,'visit_time':visit_time,'referer':referer}
        urltype = int(urltype)
        evilclass = int(evilclass)
        urlclass = int(urlclass)

        self.save2pub(dat)


    def save_url_info_with_src(self, sip,sport,fullurl, urltype, evilclass, urlclass,visit_time,referer, useragent='unknow'):
        dat = {'_dtype':2, 'sip':sip, 'sport':sport,'fullurl':fullurl, 'urltype':urltype, 'evilclass':evilclass, 'urlclass':urlclass, 'useragent':useragent,'visit_time':visit_time,'referer':referer}
        urltype = int(urltype)
        evilclass = int(evilclass)
        urlclass = int(urlclass)

        self.save2pub(dat)


    def filter_bypass(self, data):
        if data is None:
            return
        if int(data['_dtype'])==2:
            urltype = int(data['urltype'])
            evilclass = int(data['evilclass'])

            if urltype!=2:
                return True

    def save2pub(self, data):
        if self.is_filter and self.filter_bypass(data):
            return
        # we need check 404 to redirect

        self.redis_snapshot.rpush(self.save_log_pub_fullurl_detail, data)

        if self.redobj==None:
            logging.error('self.redobj error:%s',data)
        if gputils.show_noisy_logging() and time.strftime('%S') > '58':
            logging.info('pushing data %s', str(data))
        self.redobj.publish(self.save_log_pub_channel, (data))



_publisher_obj =None

def init():
    global _publisher_obj
    _publisher_obj = publisher()
    _publisher_obj.init()

def get_obj():
    global _publisher_obj
    return _publisher_obj

def save_url_info(sip,sport,fullurl, urltype, evilclass, urlclass,referer, useragent='unknow'):
    global _publisher_obj
    _publisher_obj.save_url_info(sip,sport,fullurl, urltype, evilclass, urlclass,referer, useragent)

def save5element(sip,sport,prot, dip, dport):
    global _publisher_obj
    _publisher_obj.save5element(sip,sport,prot, dip, dport)

def save_url_info_with_src(sip, sport, fullurl, urltype, evilclass, urlclass, visit_time, referer,useragent='unknow'):
    global _publisher_obj
    _publisher_obj.save_url_info_with_src(sip, sport, fullurl, urltype, evilclass, urlclass, visit_time, referer,useragent)

_check_black_redis=None
_check_unknow_redis=None

def handle_url(sip,sport, host,req, useragent, referer):


    global _check_black_redis
    global _check_unknow_redis
    try:
        if _check_black_redis is None:
            _check_black_redis = gputils.get_black_redis()
            _check_unknow_redis = gputils.get_unknow_redis()
        if _check_black_redis is None:
            return

        val2 = _check_black_redis.hmget(host, ['urltype','evilclass', 'urlclass'])


        urltype = 0
        evilclass = 0
        urlclass = 0
        fullurl = host + req
        # unknow url
        if val2 is None or val2[0] is None:
            if _check_unknow_redis is None:
                logging.error('_check_unknow_redis is None 1')
                return
            host = gputils.make_real_host(host.lower())
            _check_unknow_redis.sadd(gputils.get_unknow_redis_keyname(), host)
            save_url_info(sip,sport,fullurl, urltype, evilclass, urlclass, referer, useragent)
            return

        urltype     = val2[0]
        evilclass   = val2[1]
        urlclass    = val2[2]
        save_url_info(sip,sport,fullurl, urltype, evilclass, urlclass, referer, useragent)

    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
        print 'except ,continue'
        _check_black_redis = gputils.get_black_redis()
        _check_unknow_redis = gputils.get_unknow_redis()

from mimetools import Message
from StringIO import StringIO

def find_req_from_httppayload(httppayload):



    try:
        Referer=''
        useragent=""
        host=""
        req =""
        request_line, headers_alone = httppayload.split('\r\n', 1)
        headers = Message(StringIO(headers_alone))
        sp = request_line.split()

        if headers.has_key('Host'):
            host = headers['Host'].lower()
        if headers.has_key('User-Agent'):
            useragent = headers['User-Agent'].lower()
        if headers.has_key('Referer'):
            Referer = headers['Referer'].lower()
        if sp and len(sp)>2:
            req = sp[1] #little bug
        ret = [host, req.lower(),useragent,Referer]
        return ret
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
        logging.info('parse http:%s', str(httppayload))
        return None


gIgnore_time =time.time()
gInterval_time = 45*1000*60
gInterval_time_eff_ = 2*1000

def handle(pkt):

    tcpdat = pkt[TCP]
    if tcpdat.dport!=80:
         return
    ipdat = pkt[IP]

    save5element(ipdat.src, tcpdat.sport, 6, ipdat.dst, tcpdat.dport)
    # reqlen = ipdat.len-ipdat.ihl*4-tcpdat.dataofs*4
    # if reqlen<10:
    #     if tcpdat.flags == 2:
    #         basedef.GSaveLogRedisPub.save5element(ipdat.src, tcpdat.sport, 6, ipdat.dst, tcpdat.dport)
    #     return

    #SYN = 0x02  1st of handsharks

    #httpreq = str(pkt[TCP])
    if not pkt.haslayer(Raw):
        return
    httppayload = pkt.getlayer(Raw).load

    if not httppayload.startswith('GET /'):
        return

    req = find_req_from_httppayload(httppayload)
    if req is None:
        return

    if req[0] is not None:
        req[0] = gputils.make_real_host(req[0].lower())
    # save visit range to redis
    if req[0] is not None:
        ranghost = req[0]
        if req[0].startswith("www."):
            ranghost = ranghost[4:]
        if ranghost.endswith("/"):
            ranghost = ranghost[:-1]

        url_redis_matcher.gRedisObj.zincrby('visit_host_range', ranghost, 1)
        timeNow = datetime.now()
        record_name = 'visit_host_range' + timeNow.strftime('%Y-%m-%d')
        url_redis_matcher.gRedisObj.zincrby(record_name, ranghost, 1)

    if len(req[1])>300:
        return

    req_postfix = req[1][-5:]
    pos = req_postfix.find('.')
    if pos!=-1:
        if req_postfix[pos:] in  basedef.gvar['ignorepostfix']:
            return

    host1 = req[0]
    useragent = req[2]

    if host1.endswith('.gov') or host1.endswith('.gov.cn'):
        if basedef.GSaveLogRedisPub:
            save_url_info(host1+req[1], 3,0, 9,useragent)
        return

    if host1.endswith('.edu.cn'):
        if basedef.GSaveLogRedisPub:
            save_url_info(host1+req[1], 3,0, 10,useragent)
        return

    short_host = None
    if host1 in basedef.gvar['ignorehost'].keys():
        if basedef.GSaveLogRedisPub:
            save_url_info(host1+req[1], 3,0, basedef.gvar['ignorehost'][host1], useragent)
        return

    elif not host1.endswith('.com.cn'):
        dot1 = host1.rfind(".")
        dot2 = host1[:dot1-1].rfind(".")
        #host is not ip examed by host1[dot1+1:].isdigit()
        if dot1 !=-1 and dot2 !=-1 and dot1!=dot2 and not host1[dot1+1:].isdigit():
            short_host = host1[dot2+1:]
            if short_host in basedef.gvar['ignorehost'].keys():
                if basedef.GSaveLogRedisPub:
                    save_url_info(host1 + req[1], 3, 0, basedef.gvar['ignorehost'][short_host], useragent)
                return


    handle_url(ipdat.src, tcpdat.sport, host1, req[1],useragent, req[3])




