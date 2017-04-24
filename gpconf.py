# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import logging
import logging.handlers
import platform
import thread
import time
import urllib2
from conf import configer
import netifaces as netif

import mylogging
import os
import  gputils
import sys

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
     myconfiger = configer.Xconfiger()
     blogging = True

     def output_log(self):
         return self.blogging


     def init(self):
        import os
        if os.path.isfile('nolog'):
            self.blogging = False
            logging.info('no logging'.center(50,'*'))

        if self.binit :
             return self.binit


        self.binit  =True
        self.myconfiger.init()

     def get_direct_info(self, host,req):
         r = self.myconfiger.check_url_match(host, req)
         return  r


gcServer = confserver()

if __name__ == "__main__":
    mylogging.setuplog('gpconfig')
    print netif.interfaces()