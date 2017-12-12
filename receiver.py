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
import gputils

save_con=None
class SaveLogging2Mysql(object):

    save_log_pub_redis_num=0
    save_log_pub_channel=''
    redobj = None
    ps =None
    dbobj=None
    conn=None
    trans_data=[]
    url_data=[]
    stoprecv=None

    def init(self,save_log_pub_channel, save_log_pub_redis_num):
        self.save_log_pub_redis_num =   save_log_pub_redis_num
        self.save_log_pub_channel   =   save_log_pub_channel
        self.redobj = redis.Redis(db=save_log_pub_redis_num)
        self.ps = self.redobj.pubsub()
        self.ps.subscribe(save_log_pub_channel)

        self.init_mysql()
        basedef.GWARNING =gpwarning.Warning()
        basedef.GWARNING.init()


    def fire_saveing(self):
        logging.warn('fire saveing')
        if self.redobj:
            self.redobj.publish(self.save_log_pub_channel, {'_dtype':999})

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
            ip2int = lambda x: sum([256 ** j * int(i) for j, i in enumerate(x.split('.')[::-1])])
            sip = data['sip']
            dip = data['dip']

            if type(sip)==type('') and sip.find(".") != -1:
                sip = ip2int(sip)

            if type(dip)==type('') and dip.find(".")!=-1:
                dip = ip2int(dip)

            result = self.dbobj.execute(ins+" values(%s,%s,%s,%s,%s,%s)",(sip,data['sport'],data['prot'],dip,data['dport'],data['visit_time']))
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            self.init_mysql()
            if basedef.GWARNING: basedef.GWARNING.sendmail(str(e), traceback.format_exc())
            return




    def save2fullurl(self,data):
        if self.dbobj is None:
            return
        timeNow = datetime.datetime.now()
        tbl_name = 'fullurl_' + timeNow.strftime('%Y_%m_%d')

        ins = 'insert into {0} (sip, sport, fullurl,urltype, evilclass ,urlclass, referer, user_agent,visit_time)'.format(tbl_name)

        try:
            ip2int = lambda x: sum([256 ** j * int(i) for j, i in enumerate(x.split('.')[::-1])])
            sip = data['sip']

            if type(sip)==type('') and sip.find(".") != -1:
                sip = ip2int(sip)

            values = (sip, data['sport'], data['fullurl'], data['urltype'], data['evilclass'], data['urlclass'],
            data['referer'],data['useragent'], data['visit_time'])
            result = self.dbobj.execute(ins+" values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",values)
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            self.init_mysql()
            if basedef.GWARNING: basedef.GWARNING.sendmail(str(e), traceback.format_exc())
            return

    def go(self):

        number=0
        number_url=0
        for item in self.ps.listen():
            if item['type']!='message':
                continue

            if self.stoprecv:
                continue

            msg = item['data']
            data = eval(msg)
            if data['_dtype']==1:
                number = number + 1
                self.trans_data.append(data)
                #self.save2transIP(data)
            if data['_dtype']==2:
                number = number + 1
                number_url=number_url+1
                self.url_data.append(data)
                #self.save2fullurl(data)

            #save data
            if data['_dtype']==999 and self.conn:
                logging.info('save new data :%s, number_url:%s', number, number_url)
                number = 0
                number_url=0

                self.saveit()

            if number>50000 and self.conn:
                logging.info('save new data :%s', number)
                number=0
                number_url=0
                self.saveit()

    def saveit(self):
        self.init_mysql()
        tmptran = self.trans_data
        self.trans_data = []
        tmpurl = self.url_data
        self.url_data = []
        for data in tmptran:
            self.save2transIP(data)
        for data in tmpurl:
            self.save2fullurl(data)
        self.conn.commit()

    def stopit(self):
        self.stoprecv=True


import mylogging
sqlsaveobj=None

def clean_onexit():
    print 'exit ', sys.argv
    global sqlsaveobj
    if sqlsaveobj:
        logging.info('do the last db commit 2')
        sqlsaveobj.stopit()
        sqlsaveobj.saveit()
        time.sleep(2)
    os._exit(1)


def handle_cmd(data):
    if gputils.is_cmd_go_die(data):
        clean_onexit()
        return
    if data=='firesaveing':
        global sqlsaveobj
        sqlsaveobj.fire_saveing()


if __name__ == '__main__':
    #can only has one receiver,since we receive data by subscribe-system
    mylogging.setuplog('receiver.txt')
    import gpconf
    gpconf.make_gcs()
    basedef.GCS.init()

    cfgobj = basedef.GCS.get_config_obj()
    save_log_pub_redis_num = cfgobj.getint('boot','save_log_pub_redis_num')
    save_log_pub_channel = cfgobj.get('boot','save_log_pub_channel')

    gputils.start_listen_cmd(handle_cmd)
    obj = SaveLogging2Mysql()
    sqlsaveobj = obj
    obj.init([save_log_pub_channel], save_log_pub_redis_num)
    obj.go()
    if obj.conn:
        logging.info('do the last db commit')
        obj.conn.commit()
