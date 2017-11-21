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
import zmq

def send_cmd(cmd):
    context = zmq.Context()

    socket = context.socket(zmq.PUSH)
    bindaddr = "ipc:///tmp/guideprotect.mq.update_cfg"
    print bindaddr
    socket.connect(bindaddr)

    socket.send_string(cmd)

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
    fp_all404  = open("/tmp/all404.txt","a")
    timeNow = datetime.datetime.now()
    lasttime = timeNow + datetime.timedelta(days=-1)
    tbl_name = 'fullurl_' + lasttime.strftime('%Y_%m_%d')
    query = '''select fullurl, urltype from '''+tbl_name
    obj = db.get_create_db('transport_visit')
    r = obj.execute(query)
    result = obj.fetchall()
    url_checked =[]
    count404 =0
    checkcount = 0
    for row in result:
        url = row[0]
        if url in url_checked:
            continue
        urltype = row[1]
        if urltype and int(urltype)!=2:
            url_checked.append(url)
            is404 = is_url_404(url)
            checkcount=checkcount+1
            if is404:
                fp.write(url+"\n")
                fp_all404.write(url+"\n")
                count404 = count404+1
    logging.info('checkcount:%s ,404 count:%s', checkcount, count404)
    fp_all404.close()

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

        try:
            checkhistory()
            logging.info('done today')

            if job_hour>=1 and job_hour<7:
                send_cmd("update_cfg")

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            print 'except ,continue'


def clean_onexit():
    print 'exit ',sys.argv
    os._exit(1)

def listen_exit(name):
    import redis
    redobj = redis.Redis()
    ps = redobj.pubsub()
    ps.subscribe("exitpygp")
    for item in ps.listen():
        print item
        if item['type'] != 'message':
            continue
        msg = item['data']
        print msg
        if msg=="ok":
            clean_onexit()
            return

def start_listen_exit():
    import thread
    try:
        thread.start_new_thread(listen_exit, ('listen_exit',))
    except:
        print "Error: unable to start start_listen_exit"


if __name__ == '__main__':
    mylogging.setuplog('check404.txt')
    gpconf.make_gcs()
    basedef.GCS.init()
    clock=3
    if len(sys.argv)==2:
        clock = int(sys.argv[1])
    logging.info('clock:%s', clock)
    start_listen_exit()
    setup_3am_job(clock)