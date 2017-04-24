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
        pass
        start(snife)
    else:
        logging.info('no eth selected!!')
    logging.info('guideprotect down!')

#p = sub.Popen(('sudo', 'tcpdump', '-w'),stdout=sub.PIPE)

