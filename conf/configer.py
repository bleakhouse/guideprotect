# -*- coding: UTF-8 -*-
import json
import logging
import logging.handlers
import platform
import thread
import time
import urllib2
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from dbase import db
import basedef



class Xconfiger:

    #rulename =key, value=rule list
    dictRules={}

    def init(self):
        self.load_url_rules()
        logging.info('load rules:'+str(len(self.dictRules)))

    def load_url_rules(self):
        dictRules = {}
        dbobj =db.getDbOrCreate()
        query = '''select * from redirecturlrules'''
        dbobj.execute(query)
        result = dbobj.fetchall()
        for item in result:
            v={}
            rulename = item[1]
            if len(rulename)==0:
                rulename = "通用保护重定向"
            ruleitem = basedef.InterceptRule()

            v['name'] = rulename
            v['host'] = item[2]
            v['RedirectType'] = item[3]
            v['reqrule'] = item[4]
            v['newurldata'] = item[5]
            v['urlMatchMethod'] = item[6]

            ruleitem.strRedirectData    = v['newurldata']
            ruleitem.strRedirectType    = v['RedirectType']
            ruleitem.mstrUrlHost        = v['host'].upper()
            ruleitem.strUrlReq          = v['reqrule'].upper()
            ruleitem.strMatchMethod     = v['urlMatchMethod']
            ruleitem.strRuleName         = v['name']
            if ruleitem.mstrUrlHost.startswith('HTTP://'):
                ruleitem.mstrUrlHost =ruleitem.mstrUrlHost[7:]
            l=[]
            l.append(ruleitem)
            if rulename in self.dictRules.keys():
                self.dictRules[rulename].append(v)
            else:
                self.dictRules[rulename] = l

    def check_url_match(self, host, req):
        for name, rules  in self.dictRules.items():
            for ruleitem in rules:
                if ruleitem.is_url_match(host, req) == True:
                    rtype, rdata = ruleitem.get_redirect_info()
                    return  [rtype,rdata]

if __name__=='__main__':
    x = Xconfiger()
    x.load_url_rules()
    x.check_url_match('11','bb')