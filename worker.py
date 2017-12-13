# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging

import netifaces as netif
import os
import mylogging

import gputils
import gpconf
import snifhandler
from scapy.all import *
import visit_record
import basedef
import  gpconf
import  ignoremgr
from dbase import db
import url_redis_matcher
import ConfigParser
import gpwarning
import save_log_redis
import redis
import base64
import basedef
import datetime

import handle_packet

basedef.gvar['url_visit_count'] = 0
basedef.gvar['url_block_count'] = 0
basedef.gvar['host_visited'] = {}
basedef.gvar['blocked_host_visited'] = {}
basedef.gvar['calling_hotpath'] = False
basedef.gvar['ignorepostfix'] = set()
basedef.gvar['ignorehost'] = {}

def swap32(x):
    return (((x << 24) & 0xFF000000) |
            ((x <<  8) & 0x00FF0000) |
            ((x >>  8) & 0x0000FF00) |
            ((x >> 24) & 0x000000FF))

def checkmsg(msg):
    newpkt=""
    try:
        decode_msg = base64.b64decode(msg)
        httpreq = decode_msg[16:]
        ipinfo = struct.unpack('''4i''', decode_msg[0:16])
        sip = swap32(ipinfo[0])
        dip = swap32(ipinfo[1])
        sport = (ipinfo[2])
        dport = (ipinfo[3])
        newpkt = IP(src=sip, dst=dip) / TCP(sport=sport, dport=dport) / httpreq
        handle_packet.handle(newpkt)
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
        return



def sniff_with_redis():

    obj = redis.Redis()

    while 1:
        msg = obj.blpop('visitinginfo')
        if msg is None:
            print "msg is None"
            continue
        checkmsg(msg[1])

def clean_onexit():

    logging.info('guideprotect down!')
    logging.info('star saving redis......:%s', str(sys.argv))

    gputils.get_black_redis().save()

    logging.info('end saving redis..!')
    os._exit(1)

def handle_cmd(data):
    if gputils.is_cmd_go_die(data):
        clean_onexit()
        return
    msg  =gputils.extra_cmd_msg(data)
    if msg.startswith('noisy_'):
        gputils.set_noisy_logging(msg)


if __name__ == '__main__':

    mylogging.setuplog('guideprotect')
    reload(sys).setdefaultencoding("utf8")
    if len(sys.argv)>=2 and sys.argv[1].find('test')!=-1:
        basedef.GCFG = 'guideprotect - test.conf'
        logging.info('enter testing mode')

    logging.info('guideprotect up.....')

    ignoremgr.init()
    gpconf.make_gcs()
    basedef.GCS.init()
    basedef.GWARNING =gpwarning.Warning()
    basedef.GWARNING.init()
    handle_packet.init()

    db.createalltables()

    gputils.start_listen_cmd(handle_cmd)
    sniff_with_redis()
    clean_onexit()

#p = sub.Popen(('sudo', 'tcpdump', '-w'),stdout=sub.PIPE)

