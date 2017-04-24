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
        if len(self.dictRules)==0:
            logging.error('\n\n**********there is no ruls!!!!!!************\n\n')
        else:
            logging.info('load rules:'+str(len(self.dictRules)))

    def load_url_rules(self):
        self.dictRules = {}
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
            v['full_url'] = item[7]

            ruleitem.strRedirectData    = v['newurldata']
            ruleitem.strRedirectType    = v['RedirectType']
            ruleitem.mstrUrlHost        = v['host'].upper()
            ruleitem.strUrlReq          = v['reqrule'].upper()
            ruleitem.strMatchMethod     = v['urlMatchMethod']
            ruleitem.strRuleName         = v['name']
            ruleitem.strfullUrl         =   v['full_url'].upper()

            full_url = v['full_url']
            if len(full_url) > 0:
                full_url = v['full_url'].upper()
                if full_url.startswith('HTTP://'):
                    full_url = full_url[7:]
                pos1 = full_url.find('/')
                if pos1 != -1:
                    ruleitem.mstrUrlHost = full_url[:pos1]
                    ruleitem.strUrlReq = full_url[pos1:]
                else:
                    ruleitem.mstrUrlHost = full_url
            else:
                if ruleitem.mstrUrlHost.startswith('HTTP://'):
                    ruleitem.mstrUrlHost = ruleitem.mstrUrlHost[7:]

            if len(ruleitem.mstrUrlHost)==0 and len(ruleitem.strUrlReq)==0:
                logging.error('wrong rule!!!!!!:'+rulename)

            l=[]
            logging.info(vars(ruleitem))
            l.append(ruleitem)
            if rulename in self.dictRules.keys():
                self.dictRules[rulename].append(ruleitem)
            else:
                self.dictRules[rulename] = l

    def check_url_match(self, host, req):
        for name, rules  in self.dictRules.items():
            for ruleitem in rules:
                if ruleitem.is_url_match(host, req) == True:
                    return ruleitem.get_redirect_info()


if __name__=='__main__':
    import mylogging
    mylogging.setuplog()
    x = Xconfiger()
    x.init()
    x.check_url_match('11','bb')