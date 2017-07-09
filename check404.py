# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging
import os
import mylogging
import traceback
import gputils

import basedef
import  gpconf

from dbase import db

import datetime
import urllib2


def is_url_404(url):
    try:
        try:
            if not url.startswith('http://'):
                url = 'http://'+url
            response = urllib2.urlopen(url)
            code = response.getcode()
            print code," ",url
        except urllib2.HTTPError, e2:
            if e2.code==404:
                print 404, " ", url
                return True

    except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())

def checkhistory():

    timeNow = datetime.datetime.now()
    record_name ="record404 "+ timeNow.strftime('%Y-%m-%d')+".txt"
    fp = open(record_name,"w")
    timeNow = datetime.datetime.now()
    lasttime = timeNow + datetime.timedelta(days=-1)
    tbl_name = 'fullurl_' + lasttime.strftime('%Y_%m_%d')
    query = '''select fullurl, urltype from '''+tbl_name
    obj = db.get_create_db('transport_visit')
    r = obj.execute(query)
    result = obj.fetchall()
    for row in result:
        url = row[0]
        urltype = row[1]
        if urltype and int(urltype)!=2:
            is404 = is_url_404(url)
            if is404:
                fp.write(url+"\n")


def setup_3am_job(job_hour):
    lasttick = 0
    while 1:
        while 1:

            hour = int(time.strftime("%H", time.localtime()))
            min = int(time.strftime("%M", time.localtime()))
            if hour == job_hour and time.time() - lasttick > 60*60*12:
                lasttick = time.time()
                logging.info(' the clock is ticking')
                break
            time.sleep(40)
            continue
        checkhistory()

if __name__ == '__main__':
    mylogging.setuplog('check404')
    gpconf.make_gcs()
    basedef.GCS.init()
    clock=1
    if len(sys.argv)==2:
        clock = int(sys.argv[1])
    logging.info('clock:%s', clock)
    setup_3am_job(clock)