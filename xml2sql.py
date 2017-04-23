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



try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from dbase import db


FILE_URL_RULES_NAME   = ('url_rule.xml')


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
        rules.append(v)

    dbobj = db.getDbOrCreate()
    number = dbobj.execute('select * from redirecturlrules')

    inp = raw_input('there are {0} records in database,\nare you sure want it be replaced by xml({1} records)?\npress 1 confirm!\n'.format(number, len(rules)))

    if not inp.isdigit():
        return
    if not (int)(inp)==1:
        return

    dbobj.execute('delete  from redirecturlrules')
    insult=0
    for rule in rules:
        ins = "insert into redirecturlrules (%s,%s,%s,%s,%s,%s)"%(RULE_ATTR_NAME_name, RULE_ATTR_NAME_req_match_method, RULE_ATTR_NAME_req,
             RULE_ATTR_NAME_redirect_target,RULE_ATTR_NAME_redirect_type, RULE_ATTR_NAME_host
             )

        insult = insult+dbobj.execute(ins+" values(%s,%s,%s,%s,%s,%s)",(
             rule[RULE_ATTR_NAME_name], rule[RULE_ATTR_NAME_req_match_method], rule[RULE_ATTR_NAME_req],
             rule[RULE_ATTR_NAME_redirect_target], rule[RULE_ATTR_NAME_redirect_type], rule[RULE_ATTR_NAME_host]))

    print 'insert succ:', insult
    print '\n\n'

import sys
if __name__=='__main__':
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
