# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import sys
import thread
import time
import logging
import traceback
import logging.handlers
import urllib2
import urllib
import json
import mylogging
import  db
import platform

URL_TYPE_FORGE = (1)

URL_TYPE_SEARCH_ENG_EVIL = (2)

urlsrcs={}
urlsrcs['forgefishing_txwz'] = 'http://txwz.qq.com/lib/index.php?m=enterprise&a=get_exsample'
urlsrcs['evelsearcheng_txwz'] = 'http://txwz.qq.com/lib/index.php?m=search&a=get_list'


def isurlin(dbobj,url):
    query ='''select * from forgeurls where url=%s'''
    dbobj.execute(query,(url,))

    result=dbobj.fetchall()
    return  len(result)


def parseforgeurl(src,urlsinfo):
    urlsinfo = urlsinfo[0]
    dbobj = db.getDbOrCreate()

    urltype = URL_TYPE_FORGE

    for urlitem in urlsinfo:
        if src=='evelsearcheng_txwz':
            bn = urlitem['engine']
            url = urlitem['url']
            urltype =URL_TYPE_SEARCH_ENG_EVIL
        else:
            bn = urlitem['bn']
            url = urlitem['n']

        url = url.upper()
        url = url.encode('utf-8')
        bn = bn.encode('utf-8')
        url = url.replace("%2F","/")
        url = url.replace("%3A",":")

        if not isurlin(dbobj, url):
            result= dbobj.execute("insert into forgeurls (urlsrc,forgewho,url,urltype) values(%s,%s,%s,%s)", (src, bn, url, urltype))


def CollectThread(name):

    pl = platform.platform()

    iround = 1
    while 1:

        for src, url in urlsrcs.items():


            logging.info('collecting..from:{0}. url:{1}..'.format(src,url))
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                logging.warning(e.code)

            res = json.load(response)
            if res['reCode']!=0:
                logging.warning('error code:'+str(res['reCode']))
                continue

            if 'data'  in res.keys():
                parseforgeurl(src,res.values())

        logging.info('round:{0} done!!!'.format(iround))
        iround = iround+1


        dbobj = db.getDbOrCreate()
        path =""
        if pl.startswith("Window") is False:
            path = '/usr/share/nginx/html/info.txt'
        else:
            path = 'g:/info.txt'
            query ='''select count(*) from forgeurls'''
            dbobj.execute(query)

        result=dbobj.fetchall()
        print result
        if result is not None and len(result)>0:
            logging.info('write count')
            count= result[0][0]
            fp = open(path,"w")
            fp.write(str(count))
            fp.close()
        time.sleep(60*60)


class deamon(object):

    def Start(self):
        try:
            thread.start_new_thread( CollectThread, ("Thread-1", ) )
        except:
            print "Error: unable to start thread"


if __name__ == '__main__':

    mylogging.setuplog()
    db.createalltables()
    CollectThread('collectforurl from tx')

