# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json

import platform
import thread
import time
import urllib2

import netifaces as netif

import mylogging
import os
import  gputils
import sys
from scapy.all import *
import gpconf
import basedef

g_redirect_count = 0
g_redirect_eth=""
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
    httpres=""
    redir_target=""
    if newtarget[0]==basedef.RULE_ATTR_NAME_redirect_type_url:

        redir_target = newtarget[1]

        httpres="""HTTP/1.1 302 Found\r\n\
                Content-Type: text/html\r\n\
                Location: {}\r\n\
                Content-Length: 0\r\n\r\n""".format(redir_target)
    elif newtarget[0]==basedef.RULE_ATTR_NAME_redirect_type_buf:
        httpres="""HTTP/1.1 200 OK\r\n\
                Content-Type: text/html\r\n\
                Content-Length: {0}\r\n\r\n{1}""".format(len(newtarget[1]),newtarget[1])
        redir_target = httpres
    else:
        logging.warning('not support for Now!!!!!')
        return

    #newack = (seq+len(httpres))&0xffffffff
    newack = seq+reqlen
    response = Ether(dst=ethsrc, src=ethdst)/IP(src=dst, dst=src)/TCP(flags="A",sport=dstport, dport=srcport,seq=ack,ack=newack)/httpres
    sendp(response, iface=g_redirect_eth)
    global  g_redirect_count
    g_redirect_count = g_redirect_count + 1
    basedef.gvar['url_block_count'] = g_redirect_count
    if gpconf.gcServer.output_log():
        print 'match:',newtarget[2]
        print 'redirect to ',redir_target

        logging.info('redirect count:'+str(g_redirect_count))
        logging.info('redirect done!!')

def find_req_from_httppayload(httppayload):

    request = gputils.HTTPRequest(httppayload)
    try:
        return [request.headers['Host'], request.path]
    except:
        return None


def log_visit_info(host,req):

    basedef.gvar['url_visit_count'] =basedef.gvar['url_visit_count']+1
    host = host.upper()
    basedef.gvar['host_visited'].add(host)


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

    #logging.info(str(req))
    #print req

    host1 = req[0].upper()
    log_visit_info(host1, req[1])

    if host1 in basedef.gvar['ignorehost']:
        return


    redirect_info = gpconf.gcServer.get_direct_info(host1, req[1])
    #print 'get_direct_info:', redirect_info
    if redirect_info is None:
        return
    #logging.info('redirect '+str(req))
    inject_back_url(pkt, redirect_info)
    basedef.gvar['blocked_host_visited'].add(host1)
