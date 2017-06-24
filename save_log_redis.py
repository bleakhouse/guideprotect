# -*- coding: UTF-8 -*-
#for logging

import subprocess as sub
import sys
import time
import thread
import logging
import basedef
import redis
import traceback
from basedef import *
import os
import MySQLdb
import datetime
import gpwarning

class SaveLogging2Redis(object):

    sip=0
    sport=0
    redobj=None
    save_log_pub_channel=''

    def init(self):
        save_log_pub_redis_num=0
        cfgobj = basedef.GCS.get_config_obj()
        save_log_pub_redis_num = cfgobj.getint('boot','save_log_pub_redis_num')
        self.save_log_pub_channel = cfgobj.get('boot','save_log_pub_channel')
        self.redobj = redis.Redis(db=save_log_pub_redis_num)
        logging.info('save_log_pub_redis_num:%s,%s', save_log_pub_redis_num, self.redobj)
        logging.info('save_log_pub_channel:%s', self.save_log_pub_channel)


    def save5element(self, sip,sport,prot, dip, dport):
        self.sip = sip
        self.sport = sport
        visit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        dat = {'_dtype':1, 'sip':sip, 'sport':sport,'prot':prot, 'dip':dip, 'dport':dport,'visit_time':visit_time}
        self.save2pub(dat)

    def save_url_info(self, fullurl, urltype, evilclass, urlclass,useragent='unknow'):
        visit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        dat = {'_dtype':2, 'sip':self.sip, 'sport':self.sport,'fullurl':fullurl, 'urltype':urltype, 'evilclass':evilclass, 'urlclass':urlclass, 'useragent':useragent,'visit_time':visit_time}
        self.save2pub(dat)

    def save_url_info_with_src(self, sip,sport,fullurl, urltype, evilclass, urlclass,visit_time, useragent='unknow'):
        dat = {'_dtype':2, 'sip':sip, 'sport':sport,'fullurl':fullurl, 'urltype':urltype, 'evilclass':evilclass, 'urlclass':urlclass, 'useragent':useragent,'visit_time':visit_time}
        self.save2pub(dat)

    def save2pub(self, data):
        if self.redobj==None:
            logging.error('self.redobj error:%s',data)
        self.redobj.publish(self.save_log_pub_channel, (data))

class SaveLogging2Mysql(object):

    save_log_pub_redis_num=0
    save_log_pub_channel=''
    redobj = None
    ps =None
    dbobj=None
    conn=None

    def init(self,save_log_pub_channel, save_log_pub_redis_num):
        self.save_log_pub_redis_num =   save_log_pub_redis_num
        self.save_log_pub_channel   =   save_log_pub_channel
        self.redobj = redis.Redis(db=save_log_pub_redis_num)
        self.ps = self.redobj.pubsub()
        self.ps.subscribe(save_log_pub_channel)

        self.init_mysql()
        basedef.GWARNING =gpwarning.Warning()
        basedef.GWARNING.init()

    def init_mysql(self):

        conn = None
        op = None
        dbname ='transport_visit'
        try:
            conn = MySQLdb.connect(basedef.GCS.MYSQL_HOST, basedef.GCS.MYSQL_USR, basedef.GCS.MYSQL_PWD, charset="utf8")

            op = conn.cursor()
            op.execute("CREATE DATABASE if not exists {0} DEFAULT CHARACTER SET 'utf8'".format(dbname))
            op.execute("use " + dbname)
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            if basedef.GWARNING: basedef.GWARNING.sendmail(str(e), traceback.format_exc())
            return

        self.dbobj = op
        self.conn = conn
        return op, conn

    def save2transIP(self, data):

        if self.dbobj is None:
            return
        timeNow = datetime.datetime.now()
        tbl_name = 'tran_' + timeNow.strftime('%Y_%m_%d')

        ins = 'insert into {0} (sip, sport, prot,dip, dport,visit_time)'.format(tbl_name)

        try:
            result = self.dbobj.execute(ins+" values(%s,%s,%s,%s,%s,%s)",(data['sip'],data['sport'],data['prot'],data['dip'],data['dport'],data['visit_time']))
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            if basedef.GWARNING: basedef.GWARNING.sendmail(str(e), traceback.format_exc())
            return




    def save2fullurl(self,data):
        if self.dbobj is None:
            return
        timeNow = datetime.datetime.now()
        tbl_name = 'fullurl_' + timeNow.strftime('%Y_%m_%d')

        ins = 'insert into {0} (sip, sport, fullurl,urltype, evilclass ,urlclass, useragent,visit_time)'.format(tbl_name)

        try:
            values = (data['sip'], data['sport'], data['fullurl'], data['urltype'], data['evilclass'], data['urlclass'],
             data['useragent'], data['visit_time'])
            result = self.dbobj.execute(ins+" values(%s,%s,%s,%s,%s,%s,%s,%s)",values)
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            if basedef.GWARNING: basedef.GWARNING.sendmail(str(e), traceback.format_exc())
            return




    def go(self):

        number=0
        for item in self.ps.listen():
            if item['type']!='message':
                continue
            number = number+1
            msg = item['data']
            data = eval(msg)
            if data['_dtype']==1:
                self.save2transIP(data)
            if data['_dtype']==2:
                self.save2fullurl(data)

            if number>500 and self.conn:
                number=0
                self.conn.commit()
import mylogging
if __name__ == '__main__':
    mylogging.setuplog('save_log_redis.txt')
    import gpconf
    gpconf.make_gcs()
    basedef.GCS.init()

    cfgobj = basedef.GCS.get_config_obj()
    save_log_pub_redis_num = cfgobj.getint('boot','save_log_pub_redis_num')
    save_log_pub_channel = cfgobj.get('boot','save_log_pub_channel')


    obj = SaveLogging2Mysql()
    obj.init([save_log_pub_channel], save_log_pub_redis_num)

    obj.go()
    if obj.conn:
        logging.info('do the last db commit')
        obj.conn.commit()
