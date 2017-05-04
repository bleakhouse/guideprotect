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

def start(sniffeth):

    logging.info('importing scapy....')

    logging.info('start sniff....')

    sniff(filter="tcp and dst port 80", iface=sniffeth, prn=snifhandler.sniff_check_http_packet)

import basedef
def RuntimEnginThread(name):
    if os.path.isfile('hotpatch.py'):
        x = __import__('hotpatch')
        x.check(basedef.gvar)
        time.sleep(30)
    while 1:
        if os.path.isfile('hotpatch.py'):
            x = reload(sys.modules['hotpatch'])
            x.check(basedef.gvar)
        else:
            print 'no patch file'
        time.sleep(30)

class RuntimEngin(object):
    def Start(self):
        try:
            thread.start_new_thread(RuntimEnginThread, ("RuntimEnginThread-1",))
        except:
            print "Error: unable to start RuntimEnginThread"



import  gpconf
if __name__ == '__main__':

    mylogging.setuplog('guideprotect')
    reload(sys).setdefaultencoding("utf8")

    logging.info('guideprotect up.....')
    gpconf.gcServer.init()
    snife, inje= gpconf.get_sniff_eth()
    if len(snife)>0 and  len(inje)>0:
        print 'select eth:'
        print 'sniffer:',snife
        print 'inject:',inje
        snifhandler.g_redirect_eth=inje
        RuntimEngin.Start()
        start(snife)
    else:
        logging.info('no eth selected!!')
    logging.info('guideprotect down!')

#p = sub.Popen(('sudo', 'tcpdump', '-w'),stdout=sub.PIPE)

