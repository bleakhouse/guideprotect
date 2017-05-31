# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging
import traceback

import os
import datetime
from dbase import db
import MySQLdb


def update_url_check_stat(ginfo):
    url_visit_count = ginfo['url_visit_count']
    blocked_host_visited = ginfo['blocked_host_visited']
    ginfo['blocked_host_visited'] = 0
    ginfo['url_visit_count'] =0

    today = db.get_today_visit_count_date()

    obj = db.getDbOrCreate()
    update = '''update url_check_stat set url_visit_count=url_visit_count+%s, url_block_count=url_block_count +%s where date=%s'''
    result = obj.execute(update, (url_visit_count, blocked_host_visited, db.get_today_visit_count_date()))

    ginfo['url_visit_count']=0
    ginfo['blocked_host_visited']=0

def get_visit_db(dbname='host_visit_rate'):
    conn=None
    op = None
    try:

        conn = MySQLdb.connect(db.MYSQL_HOST,db.MYSQL_USR,db.MYSQL_PWD,  charset="utf8")

        op = conn.cursor()
        op.execute("CREATE DATABASE if not exists {0} DEFAULT CHARACTER SET 'utf8'".format(dbname))
        op.execute("use "+dbname)
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
    return  op, conn

def update_visit_host_rate(ginfo):

    obj, conn= get_visit_db()
    today = db.get_today_host_visit_tblname()
    for host, count in ginfo['host_visited'].items():

        host = host.lower()
        query = '''select * from {0} where host_name=%s'''.format(today)
        obj.execute(query, (host,))
        result = obj.fetchall()
        if len(result)>0:
            update = '''update {} set host_visit_count=host_visit_count +%s where host_name=%s'''.format(today)
            result = obj.execute(update, (count, host))

        else:
            sql = "insert into {} (host_name,host_visit_count) values(%s,%s)".format(today)
            result = obj.execute(sql,( host,count))

    conn.commit()

    ginfo['host_visited']={}

if __name__=='__main__':
    ginfo={}
    haha={}
    haha['baidu.com']=1
    ginfo['host_visited']=haha
    update_visit_host_rate(ginfo)
    pass