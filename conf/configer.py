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
import gpconf
import os
gtestx=1
class Xconfiger:

    #rulename =key, value=rule list
    dictRules={}


    def init(self):



        self.load_url_rules()
        if len(self.dictRules)==0:
            logging.error('\n\n**********there is no ruls!!!!!!************\n\n')
        else:

            logging.info('load rules type:'+str(len(self.dictRules)))
            num =0
            for k,v in self.dictRules.items():
                num = num+1*len(v)
            logging.info('number of rules:'+str(num))
        basedef.gvar['rules_info'] = self.dictRules

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
            if v['host'] is None:
                v['host']=""
            if v['full_url'] is None:
                v['full_url']=""
            if v['reqrule'] is None:
                v['reqrule']=""

            for k2,v2 in v.items():
                v[k2] = str(v2)

            ruleitem.strRedirectData    = v['newurldata']
            ruleitem.strRedirectType    = v['RedirectType']
            ruleitem.mstrUrlHost        = v['host'].upper()
            ruleitem.strUrlReq          = v['reqrule'].upper()
            ruleitem.strMatchMethod     = v['urlMatchMethod']
            ruleitem.strRuleName         = v['name']
            ruleitem.strfullUrl         =   v['full_url'].upper()
            if ruleitem.strRedirectType==basedef.RULE_ATTR_NAME_redirect_type_buf:
                ruleitem.strRedirectData = str(ruleitem.strRedirectData)

            if  ruleitem.strRedirectType==basedef.RULE_ATTR_NAME_redirect_type_file and os.path.isfile(ruleitem.strRedirectData):
                ruleitem.strRedirectDataIfFile =  open(ruleitem.strRedirectData,'r').read()

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
                    ruleitem.strUrlReq = "/"
            else:
                if ruleitem.mstrUrlHost.startswith('HTTP://'):
                    ruleitem.mstrUrlHost = ruleitem.mstrUrlHost[7:]

            if len(ruleitem.mstrUrlHost)==0 and len(ruleitem.strUrlReq)==0:
                logging.error('wrong rule!!!!!!:'+rulename)

            l=[]

            newkey =None
            l.append(ruleitem)
            dickey = full_url
            if len(dickey)==0:
                dickey = ruleitem.mstrUrlHost
            else:
                if full_url.startswith('WWW.'):
                    newkey =full_url[4:]
                else:
                    newkey = "WWW."+full_url


            dickey = str(dickey)
            if dickey in self.dictRules.keys():
                self.dictRules[dickey].append(ruleitem)
            else:
                self.dictRules[dickey] = l

            if newkey is not None:
                l2 = []
                if newkey.startswith('WWW.'):
                    ruleitem.mstrUrlHost = "WWW."+ruleitem.mstrUrlHost
                else:
                    ruleitem.mstrUrlHost=ruleitem.mstrUrlHost[4:]

                l2.append(ruleitem)
                newkey = str(newkey)
                if newkey in self.dictRules.keys():
                    self.dictRules[newkey].append(ruleitem)
                else:
                    self.dictRules[newkey] = l

    def check_url_match(self, host, req):
        fullurl = host+req

        dickey = fullurl.upper()

        ruleitemlist = None
        if dickey in self.dictRules.keys():
            ruleitemlist = self.dictRules[dickey]
        else:
            dickey = host.upper()
            if dickey in self.dictRules.keys():
                ruleitemlist = self.dictRules[dickey]
        if ruleitemlist is None:
            return

        for ruleitem in ruleitemlist:
            if ruleitem.is_url_match(host, req) == True:
                r= ruleitem.get_redirect_info()
                ruleitem.imatch_count = ruleitem.imatch_count+1

                if gpconf.gcServer.output_log():
                    print 'is_url_match'
                    print r
                return  r


if __name__=='__main__':
    import mylogging
    mylogging.setuplog()
    x = Xconfiger()
    x.init()
    x.check_url_match('11','bb')