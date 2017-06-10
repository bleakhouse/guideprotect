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
import platform
from basedef import *
import os
import traceback
import MySQLdb


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from dbase import db


FILE_URL_RULES_NAME   = ('url_rule.xml')


def getDbOrCreate2(dbname='guideprotect'):
    conn=None
    op = None
    try:

        MYSQL_HOST = "127.0.0.1"
        MYSQL_USR = 'test'
        MYSQL_PWD = '123456'
        conn = MySQLdb.connect(MYSQL_HOST,MYSQL_USR,MYSQL_PWD,  charset="utf8")

        op = conn.cursor()
        op.execute("CREATE DATABASE if not exists {0} DEFAULT CHARACTER SET 'utf8'".format(dbname))
        op.execute("use "+dbname)
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
    return  op, conn

def restore2sql(fname=FILE_URL_RULES_NAME):

    if not os.path.isfile(fname):
        print  'no file name:',fname
        return

    tree = ET.ElementTree(file=fname)

    root = tree.getroot()
    rules=[]
    for rule  in root:
        v = {}
        v.update(rule.attrib)
        for rule_sub in rule:
            v[rule_sub.tag] = rule_sub.text
            if v[rule_sub.tag] is  not None:
                v[rule_sub.tag] = v[rule_sub.tag].lower()

        if not RULE_ATTR_NAME_host in v.keys() and not RULE_ATTR_NAME_req in v.keys():
            if not RULE_ATTR_NAME_full_url in v.keys():
                logging.error('error rule :'+v[RULE_ATTR_NAME_name])
                continue
        #these two node can be empty
        if not RULE_ATTR_NAME_host in v.keys():
            v[RULE_ATTR_NAME_host]=""

        if not RULE_ATTR_NAME_req in v.keys():
            v[RULE_ATTR_NAME_req] = ""

        rules.append(v)

    dbobj, conn = getDbOrCreate2()
    number = dbobj.execute('select * from redirecturlrules')

    inp = raw_input('there are {0} records in database,\nare you sure want it be replaced by xml({1} records)?\npress 1 confirm!\n'.format(number, len(rules)))

    if not inp.isdigit():
        return
    if not (int)(inp)==1:
        return

    dbobj.execute('delete  from redirecturlrules')
    insult=0
    for rule in rules:
        ins = "insert into redirecturlrules (%s,%s,%s,%s,%s,%s,%s)"%(RULE_ATTR_NAME_name, RULE_ATTR_NAME_req_match_method, RULE_ATTR_NAME_req,
             RULE_ATTR_NAME_redirect_target,RULE_ATTR_NAME_redirect_type, RULE_ATTR_NAME_host, RULE_ATTR_NAME_full_url
             )

        insult = insult+dbobj.execute(ins+" values(%s,%s,%s,%s,%s,%s,%s)",(
             rule[RULE_ATTR_NAME_name], rule[RULE_ATTR_NAME_req_match_method], rule[RULE_ATTR_NAME_req],
             rule[RULE_ATTR_NAME_redirect_target], rule[RULE_ATTR_NAME_redirect_type], rule[RULE_ATTR_NAME_host], rule[RULE_ATTR_NAME_full_url]))
    conn.commit()
    print 'insert succ:', insult
    print '\n\n'

import sys
import gputils

if __name__=='__main__':


    # request_text = '''GET /search?sourceid=chrome&ie=UTF-8&q=ergterst HTTP/1.1\r\nHost: www.google.com\r\nConnection: keep-alive\r\nAccept: application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5\r\nUser-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.45 Safari/534.13\r\nAccept-Encoding: gzip,deflate,sdch\r\nAvail-Dictionary: GeNLY2f-\r\nAccept-Language: en-US,en;q=0.8\r\n'''
    # #request_text = '''123123'''
    # request = gputils.HTTPRequest(request_text)
    # try:
    #
    #     print request.path  # startswith '/', liek '/search?sourceid=chrome&ie=UTF-8&q=ergterst'
    #     print request.headers['Host']
    # except:
    #     print 'error'
    print sys.argv
    try:
        if len(sys.argv)==2:
            restore2sql(sys.argv[1])
        else:
            restore2sql()
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())

    raw_input('press anykey to exit!')
