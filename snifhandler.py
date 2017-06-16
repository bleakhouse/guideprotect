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
    global g_redirect_eth
    sendp(response, iface=g_redirect_eth, verbose= False)
    global  g_redirect_count

    g_redirect_count = g_redirect_count + 1
    basedef.gvar['url_block_count'] = basedef.gvar['url_block_count']+1
    if basedef.GCS.output_log():
        print 'match:',newtarget[2]
        print 'redirect to ',redir_target

        logging.info('redirect count:'+str(g_redirect_count))
        logging.info('redirect done!!')
    return True


def find_req_from_httppayload(httppayload):

    request = gputils.HTTPRequest(httppayload)
    try:
        return [request.headers['Host'].lower(), request.path.lower()]
    except:
        return None


def log_visit_info(host,req):

    basedef.gvar['url_visit_count'] =basedef.gvar['url_visit_count']+1

    newhost = host

    if host.startswith("www."):
        newhost = host[4:]

    if newhost[-1:]=='/':
        newhost = newhost[:-1]

    if newhost in basedef.gvar['host_visited'].keys():
        basedef.gvar['host_visited'][newhost] = basedef.gvar['host_visited'][newhost]+1
    else:
        basedef.gvar['host_visited'][newhost]=1


def log_redirect_url(host,req):
    full = host+req

    if full in basedef.gvar['blocked_host_visited'].keys():
        basedef.gvar['blocked_host_visited'][full] = basedef.gvar['blocked_host_visited'][full]+1
    else:
        basedef.gvar['blocked_host_visited'][full]=1


gIgnore_time =time.time()
gInterval_time = 45*1000*60
gInterval_time_eff_ = 2*1000

def sniff_check_http_packet(pkt):

    # if not pkt.haslayer(TCP):
    #     print 'has no tcp layer'
    #     return
    #
    #这些后面过滤后，不需要，直接找req

    # global  gIgnore_time
    # global  gInterval_time
    # global  gInterval_time_eff_
    # x =time.time()-gIgnore_time
    # if x>gInterval_time:
    #     if x < gInterval_time_eff_:
    #         return
    #     else:
    #         gIgnore_time = time.time()

    if basedef.gcalling_hotpath==True:
        return

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

    if len(req[1])>300:
        return

    req_postfix = req[1][-5:]
    pos = req_postfix.find('.')
    if pos!=-1:
        if req_postfix[pos:] in  basedef.gvar['ignorepostfix']:
            return

    #logging.info(str(req))
    #print req



    host1 = req[0]
    log_visit_info(host1, req[1])

    if host1.endswith('.gov'):
        return
    if host1.endswith('.gov.cn'):
        return

    short_host = None
    if host1 in basedef.gvar['ignorehost']:
        return

    else:
        dot1 = host1.rfind(".")
        dot2 = host1[:dot1-1].rfind(".")
        if dot1 !=-1 and dot2 !=-1 and dot1!=dot2:
            short_host = host1[dot2+1:]
            if short_host in basedef.gvar['ignorehost']:
                return



    redirect_info = basedef.GCS.get_direct_info(host1, req[1],short_host)

    #print 'get_direct_info:', redirect_info
    if redirect_info is None:
        return
    #logging.info('redirect '+str(req))
    r = inject_back_url(pkt, redirect_info)

    if r==True:
        log_redirect_url(host1, req[1])

