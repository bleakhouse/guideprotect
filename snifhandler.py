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

import mylogging
import os
import  utils
import sys
from scapy.all import *
import gpconf
import basedef

g_redirect_count = 0

def inject_back_url(pkt, newtarget):

    src=pkt[IP].src
    srcport=pkt[TCP].sport
    dst=pkt[IP].dst
    dstport=pkt[TCP].dport
    ack = pkt[TCP].ack
    seq = pkt[TCP].seq

    reqlen = pkt[IP].len-pkt[IP].ihl*4-pkt[TCP].dataofs*4
    ethsrc = pkt[Ether].src
    ethdst = pkt[Ether].dst
    if newtarget[0]!=basedef.RULE_ATTR_NAME_redirect_type_url:
        logging.warning('not support for Now!!!!!')
        return

    redir_url = newtarget[1]

    httpres="""HTTP/1.1 302 Found\r\n\
            Content-Type: text/html\r\n\
            Location: {}\r\n\
            Content-Length: 0\r\n\r\n""".format(redir_url)

    print 'redirect to ',redir_url
    #newack = (seq+len(httpres))&0xffffffff
    newack = seq+reqlen
    response = Ether(dst=ethsrc, src=ethdst)/IP(src=dst, dst=src)/TCP(flags="A",sport=dstport, dport=srcport,seq=ack,ack=newack)/httpres
    sendp(response)
    global  g_redirect_count
    logging.info('redirect count:'+str(g_redirect_count))
    g_redirect_count = g_redirect_count+1

def find_req_from_httppayload(httppayload):

    request = utils.HTTPRequest(httppayload)
    try:
        return [request.path,request.headers['Host']]
    except:
        return None

def sniff_check_http_packet(pkt):

    # if not pkt.haslayer(TCP):
    #     print 'has no tcp layer'
    #     return
    #
    #这些后面过滤后，不需要，直接找req

    if pkt[TCP].dport!=80:
         return
    reqlen = pkt[IP].len-pkt[IP].ihl*4-pkt[TCP].dataofs*4
    if reqlen<10:
        return

    #httpreq = str(pkt[TCP])
    if not pkt.haslayer(Raw):
        return
    httppayload = str(pkt[Raw])

    if not httppayload.startswith('GET /'):
        return

    req = find_req_from_httppayload(httppayload)
    if req is None:
        return

    logging.info(str(req))
    print req
    gpconf.gcServer.init()
    redirect_info = gpconf.gcServer.get_direct_info(req[0], req[1])
    if redirect_info is None:
        return

    inject_back_url(pkt, redirect_info)

