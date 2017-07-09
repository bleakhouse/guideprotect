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
import basedef
import mylogging
import os
import  gputils
import sys
import traceback
import ConfigParser
import url_redis_matcher
import  url_mysql_matcher


SELECT_CONF_FILENAME ='seleth.txt'





def promote_select_eth():
    iflist = gputils.getIfaceList()
    if len(iflist) < 2:
        logging.info('there is no enough ethers')
        sys.exit(0)
    count = 1
    for i in iflist:
        log = "({0}) eth name:{1}\n\tip:{2}\n".format(count, i['name'], i['ip'])
        print(log)
        count = count + 1

    choice = raw_input('select sniff ehter:')
    if int(choice)==0 or int(choice) > len(iflist):
        print 'wrong choice'
        choice = raw_input('select sniff ehter:')
        if int(choice) == 0 or int(choice) > len(iflist):
            print 'wrong choice!!!'
            return "", ""

    sniffifeth = iflist[(int(choice)-1)]
    print("sniffer eth name:{0}".format(sniffifeth['name']))
    choice = raw_input('select inject back ehter:')
    if int(choice)==0 or int(choice) > len(iflist):
        print 'wrong choice'
        choice = raw_input('select inject back ehter:')
        if int(choice) == 0 or int(choice) > len(iflist):
            print 'wrong choice!!!'
            return "", ""

    injecteth = iflist[(int(choice)-1)]
    print("inject eth name:{0}".format(injecteth['name']))
    fp = open(SELECT_CONF_FILENAME, "w")
    fp.write(sniffifeth['ethname'].strip()+"\n")
    fp.write(injecteth['ethname'].strip()+"\n")
    fp.close()
    return sniffifeth['ethname'].strip(), injecteth['ethname'].strip()

def get_sniff_eth():

    if os.path.exists('seleth.txt'):
        fp = open(SELECT_CONF_FILENAME,'r')
        content=[]
        for l in fp:
            content.append(l)
        if len(content)!=2:
            return  promote_select_eth()
        else:
            return content[0].strip(), content[1].strip()
    else:
        print 'first time'
        return promote_select_eth()


class confserver:

     binit=False

     blogging = False
     config_obj=None
     DATABASE_NAME = 'guideprotect'
     MYSQL_HOST = "127.0.0.1"
     MYSQL_USR = 'test'
     MYSQL_PWD = '123456'
     # 0 = redis
     # 1 = mysql
     rules_src = 0
     url_mysql_obj = url_mysql_matcher.url_mysql()

     def output_log(self):
         return self.blogging

     def is_rule_from_redis(self):
         return self.rules_src == 0

     def is_rule_from_mysql(self):
         return self.rules_src==1

     def init(self):

        if self.binit :
             return self.binit


        self.paser_cfg(basedef.GCFG)
        self.binit  =True

        if self.is_rule_from_redis():
            url_redis_matcher.init_redis()
            return
        self.url_mysql_obj.init()

     def get_config_obj(self):
         return  self.config_obj


     def paser_cfg(self, cfg):

        try:
            if os.path.isfile(cfg):
                GP_Configer = ConfigParser.ConfigParser()
                GP_Configer.read(cfg)
                self.config_obj = GP_Configer
                if GP_Configer.has_option('boot', 'url_type_valid_time'):
                    url_type_valid_time = GP_Configer.getint('boot', 'url_type_valid_time')
                    basedef.GP_URL_TYPE_VALID_TIMES = url_type_valid_time * 24 * 3600
                    logging.info('url_type_valid_time(days):%s', url_type_valid_time)
                    logging.info('GP_URL_TYPE_VALID_TIMES(sec):%s', basedef.GP_URL_TYPE_VALID_TIMES)

                if GP_Configer.has_option('boot', 'logging'):
                    self.blogging = GP_Configer.getint('boot', 'logging')==1

                if GP_Configer.has_option('boot', 'logging'):
                    src = GP_Configer.getint('boot', 'rule_src')
                    if src == 0 or src==1:
                        self.rules_src =src
                    print 'rules_src:', self.rules_src
                if GP_Configer.has_option('boot', 'mysql_host') and \
                    GP_Configer.has_option('boot', 'mysql_user') and \
                    GP_Configer.has_option('boot', 'mysql_password'):
                    self.MYSQL_HOST = GP_Configer.get('boot', 'mysql_host')
                    self.MYSQL_USR = GP_Configer.get('boot', 'mysql_user')
                    self.MYSQL_PWD = GP_Configer.get('boot', 'mysql_password')
                print 'mysql info:'
                print 'mysql MYSQL_HOST:',self.MYSQL_HOST
                print 'mysql MYSQL_USR:',self.MYSQL_USR
                print 'mysql MYSQL_PWD:',self.MYSQL_PWD

            else:
                 logging.info('url_type_valid_time(days):%s', basedef.GP_URL_TYPE_VALID_TIMES / 3600 / 24)

                 logging.warning('not found:%s', cfg)

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())

     def get_direct_info(self, host,req, useragent, referer,short_host=None ):

        if self.is_rule_from_redis():
            r= url_redis_matcher.get_direct_info(host, req, useragent, referer, short_host)
        else:
            r = url_mysql_matcher.get_direct_info(host, req)
        return  r

def make_gcs():
    basedef.GCS = confserver()


if __name__ == "__main__":
    mylogging.setuplog('gpconfig')
    print netif.interfaces()