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

import basedef
basedef.gvar['url_visit_count'] = 0
basedef.gvar['url_block_count'] = 0
basedef.gvar['host_visited'] = set()
basedef.gvar['blocked_host_visited'] = set()
basedef.gvar['calling_hotpath'] = False

def start(sniffeth):

    logging.info('importing scapy....')

    logging.info('start sniff....')

    sniff(filter="tcp and dst port 80", iface=sniffeth, prn=snifhandler.sniff_check_http_packet)

import basedef
def RuntimEnginThread(name):

    try:
        if os.path.isfile('hotpatch.py'):
            x = __import__('hotpatch')
            x.check(basedef.gvar)
            time.sleep(30)
    except:
        print "Error: RuntimEnginThread 1"
    while 1:
        try:
            if os.path.isfile('hotpatch.py'):
                logging.info('calling hotpath')

                basedef.gvar['calling_hotpath'] = True
                x = __import__('hotpatch')
                x = reload(sys.modules['hotpatch'])
                x.check(basedef.gvar)
                logging.info('end call hotpath')
                basedef.gvar['calling_hotpath'] = False
            else:
                print 'no patch file'
            time.sleep(30)
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())

            time.sleep(30)
            continue


class RuntimEngin(object):
    def Start(self):
        try:
            thread.start_new_thread(RuntimEnginThread, ("RuntimEnginThread-1",))
        except:
            print "Error: unable to start RuntimEnginThread"


def init_ignore_host_list():

    basedef.gvar['ignorehost'] = set()

    if not os.path.isfile('ignorehost.txt'):
        return
    fp = open('ignorehost.txt', 'r')
    for r in fp:
        r = r.strip()
        if len(r)==0:
            continue
        basedef.gvar['ignorehost'].add(r)
    logging.info("init ignor host list:"+str(len(basedef.gvar['ignorehost'])))


import  gpconf
if __name__ == '__main__':

    mylogging.setuplog('guideprotect')
    reload(sys).setdefaultencoding("utf8")
    init_ignore_host_list()
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

