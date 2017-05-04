# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import logging
import logging.handlers
import platform
import thread
import time
import re
import os


RULE_ATTR_NAME_rule = 'rule'
RULE_ATTR_NAME_name = 'name'
RULE_ATTR_NAME_host = 'host'
RULE_ATTR_NAME_req = 'req'
RULE_ATTR_NAME_redirect_target = 'redirect_target'
RULE_ATTR_NAME_redirect_type = 'redirect_type'
RULE_ATTR_NAME_req_match_method = 'req_match_method'
RULE_ATTR_NAME_full_url = 'full_url'

RULE_ATTR_NAME_req_match_method_same   = "same"
RULE_ATTR_NAME_req_match_method_starts   = "startswith"
RULE_ATTR_NAME_req_match_method_regexp   = "regexp"


RULE_ATTR_NAME_redirect_type_url  ='url'
RULE_ATTR_NAME_redirect_type_buf  ='buf'
RULE_ATTR_NAME_redirect_type_file  ='file'

gvar={}

#type for strRedirectType 'url', 'buf','buffile'
class InterceptRule:
    mstrUrlHost =""
    strUrlReq=""
    strRedirectType=RULE_ATTR_NAME_redirect_type_url
    strRedirectData=""
    strMatchMethod =RULE_ATTR_NAME_req_match_method_same
    strRuleName="default"
    repattern=None
    strRedirectDataIfFile=None
    strfullUrl=""
    imatch_count=0
    def is_url_match(self, host, req):

        host = host.upper()
        if host!=self.mstrUrlHost and len(self.mstrUrlHost)>0:
            return  False

        req = req.upper()
        if len(self.strUrlReq)==0:
            return  True

        if self.strMatchMethod == RULE_ATTR_NAME_req_match_method_same:
            if self.strUrlReq==req:
                return True
            return False

        if self.strMatchMethod ==RULE_ATTR_NAME_req_match_method_starts:
            if req.startswith(self.strUrlReq):
                return True
            return False

        if self.strMatchMethod == RULE_ATTR_NAME_req_match_method_regexp:
            if self.repattern is None:
                self.repattern = re.compile(self.strUrlReq)
            r = self.repattern.search(req)
            if r is not None:
                return True

        return  False


    def get_redirect_info(self):

        if self.strRedirectDataIfFile is not None:
            return [RULE_ATTR_NAME_redirect_type_buf, self.strRedirectDataIfFile,self.strRuleName]

        if self.strRedirectType==RULE_ATTR_NAME_redirect_type_file:
            self.strRedirectType = RULE_ATTR_NAME_redirect_type_buf
            if os.path.isfile(self.strRedirectData):
                self.strRedirectDataIfFile =  open(self.strRedirectData,'r').read()
                return [RULE_ATTR_NAME_redirect_type_buf, self.strRedirectDataIfFile, self.strRuleName]
            else:
                logging.error('file not exits '+self.strRedirectData)
                return [RULE_ATTR_NAME_redirect_type_buf,'no data error03',self.strRuleName]

        return [self.strRedirectType, self.strRedirectData,self.strRuleName]

