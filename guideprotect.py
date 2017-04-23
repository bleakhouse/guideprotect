# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging

import netifaces as netif
import os
import mylogging

import utils
import gpconf
import snifhandler

def start():

    logging.info('importing scapy....')

    logging.info('start sniff....')
    from scapy.all import *
    sniff(filter="tcp and port 80 and host 192.168.64.128", prn=snifhandler.sniff_check_packet)


if __name__ == '__main__':

    mylogging.setuplog('guideprotect')
    reload(sys).setdefaultencoding("utf8")

    logging.info('guideprotect up.....')

    snife, inje= gpconf.get_sniff_eth()
    if len(snife)>0 and  len(inje)>0:
        print 'select eth:'
        print 'sniffer:',snife
        print 'inject:',inje
        pass
        #start()
    else:
        logging.info('no eth selected!!')
    logging.info('guideprotect down!')

#p = sub.Popen(('sudo', 'tcpdump', '-w'),stdout=sub.PIPE)

