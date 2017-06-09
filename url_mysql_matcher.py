# -*- coding: UTF-8 -*-
import json
import logging
import logging.handlers
import platform
import thread
import time
import urllib2
import basedef
import os
from conf import configer




class url_mysql(object):
    myconfiger = configer.Xconfiger()

    def init(self):
        self.myconfiger.init()

    def get_direct_info(self, host, req):
        return self.myconfiger.check_url_match(host, req)

if __name__=='__main__':
    pass