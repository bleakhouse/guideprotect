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



def init_ignore_host_list():

    basedef.gvar['ignorehost'] = {}

    if not os.path.isfile('ignorehost.txt'):
        return
    fp = open('ignorehost.txt', 'r')
    for r in fp:
        r = r.strip()
        if r.startswith("#"):
            continue
        if len(r)==0:
            continue
        info = r.split(',')
        if len(info)!=2:
            logging.error('error ignore host:%s', str(info))
            continue
        if info[0].lower() not in basedef.gvar['ignorehost'].keys():
            basedef.gvar['ignorehost'][info[0].lower()] =int(info[1])
    logging.info("init ignor host list:%s",len(basedef.gvar['ignorehost']))

def init_ignore_postfix_list():

    basedef.gvar['ignorepostfix'] = set()

    if not os.path.isfile('ignorepostfix.txt'):
        return
    fp = open('ignorepostfix.txt', 'r')
    for r in fp:
        r = r.strip()
        if r.startswith("#"):
            continue
        if len(r)==0:
            continue
        basedef.gvar['ignorepostfix'].add(r.lower())
    logging.info("init ignor ignorepostfix list:"+str(len(basedef.gvar['ignorepostfix'])))

def init():
    init_ignore_host_list()
    init_ignore_postfix_list()
