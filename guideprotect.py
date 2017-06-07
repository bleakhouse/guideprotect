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

basedef.gvar['url_visit_count'] = 0
basedef.gvar['url_block_count'] = 0
basedef.gvar['host_visited'] = {}
basedef.gvar['blocked_host_visited'] = {}
basedef.gvar['calling_hotpath'] = False
basedef.gvar['ignorepostfix'] = set()
basedef.gvar['ignorehost'] = set()

def start(sniffeth):

    logging.info('importing scapy....')

    logging.info('start sniff....')

    sniff(filter="tcp and dst port 80", iface=sniffeth, prn=snifhandler.sniff_check_http_packet)

import basedef

import datetime


def RuntimEnginThread(name):
    MAX_SLEEP = 30 * 60
    try:
        if os.path.isfile('hotpatch.py'):
            x = __import__('hotpatch')
            x.check(basedef.gvar)
            time.sleep(10)
    except:
        print "Error: RuntimEnginThread 1"
    while 1:
        try:
            basedef.gcalling_hotpath = True

            if os.path.isfile('hotpatch.py'):
                #logging.info('calling hotpath')

                x = __import__('hotpatch')
                x = reload(sys.modules['hotpatch'])
                x.check(basedef.gvar)
                #logging.info('end call hotpath')

            else:
                print 'no patch file'

            visit_record.update_url_check_stat(basedef.gvar)

            visit_record.update_visit_host_rate(basedef.gvar)

            basedef.gcalling_hotpath = False
            db.create_visit_furture_record()

            time.sleep(MAX_SLEEP)

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            basedef.gcalling_hotpath = False
            time.sleep(30)
            continue


class RuntimEngin(object):
    def Start(self):
        try:
            thread.start_new_thread(RuntimEnginThread, ("RuntimEnginThread-1",))
        except:
            print "Error: unable to start RuntimEnginThread"



if __name__ == '__main__':

    mylogging.setuplog('guideprotect')
    reload(sys).setdefaultencoding("utf8")

    ignoremgr.init()
    url_redis_matcher.init_redis()

    logging.info('guideprotect up.....')
    gpconf.gcServer.init()
    snife, inje= gpconf.get_sniff_eth()
    if len(snife)>0 and  len(inje)>0:
        print 'select eth:'
        print 'sniffer:',snife
        print 'inject:',inje
        snifhandler.g_redirect_eth=inje
        RuntimEngin().Start()
        start(snife)
    else:
        logging.info('no eth selected!!')
    logging.info('guideprotect down!')

#p = sub.Popen(('sudo', 'tcpdump', '-w'),stdout=sub.PIPE)

