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
import MySQLdb
import basedef
import datetime

DATABASE_NAME  = 'guideprotect'
MYSQL_HOST="127.0.0.1"
MYSQL_USR = 'test'
MYSQL_PWD = '123456'

def getDbOrCreate(dbname=DATABASE_NAME):

    obj=None
    op = None
    try:

        obj = MySQLdb.connect(MYSQL_HOST,MYSQL_USR,MYSQL_PWD,  charset="utf8")

        obj.autocommit(1)
        op = obj.cursor()
        op.execute("CREATE DATABASE if not exists {0} DEFAULT CHARACTER SET 'utf8'".format(dbname))
        op.execute("use "+dbname)
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
    return  op


def get_create_host_visitdb(dbname='host_visit_rate'):

    obj=None
    op = None
    try:

        obj = MySQLdb.connect(MYSQL_HOST,MYSQL_USR,MYSQL_PWD,  charset="utf8")

        obj.autocommit(1)
        op = obj.cursor()
        op.execute("CREATE DATABASE if not exists {0} DEFAULT CHARACTER SET 'utf8'".format(dbname))
        op.execute("use "+dbname)
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
    return  op


forgeurls='''CREATE TABLE forgeurls (
  Id bigint(21) NOT NULL auto_increment,
  urlsrc varchar(128) NOT NULL default '',
  forgewho varchar(128) NOT NULL default '',
  url varchar(1024) NOT NULL default '',
  urltype bigint(32),
  AddTime timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY  (Id),
  KEY UserName (urlsrc)
) ENGINE=InnoDB, character set = utf8;;
'''


redirecturlrules='''CREATE TABLE redirecturlrules (
  Id bigint(21) NOT NULL auto_increment,
  {0} varchar(128) NOT NULL default '',
  {1} varchar(128) default '',
  {2} varchar(128) NOT NULL default '',
  {3} varchar(128) default '',
  {4} varchar(1024) NOT NULL default '',
  {5} varchar(1024) NOT NULL default '',
  {6} varchar(1024) NOT NULL default '',
  AddTime timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY  (Id)
) ENGINE=InnoDB, character set = utf8;;
'''.format(basedef.RULE_ATTR_NAME_name, basedef.RULE_ATTR_NAME_host, basedef.RULE_ATTR_NAME_redirect_type, basedef.RULE_ATTR_NAME_req,
           basedef.RULE_ATTR_NAME_redirect_target, basedef.RULE_ATTR_NAME_req_match_method,basedef.RULE_ATTR_NAME_full_url)

url_check_stat='''CREATE TABLE url_check_stat (
  Id bigint(21) NOT NULL auto_increment,
  url_visit_count bigint(32),
  url_block_count bigint(32),
  check_date DATETIME,
  PRIMARY KEY  (Id)
) ENGINE=InnoDB, character set = utf8;;
'''



def createtable(table_create_sql):

    db =getDbOrCreate(DATABASE_NAME)

    if db is None:
        logging.info('getDbOrCreate fail')
        return
    try:
        db.execute(table_create_sql)

    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    else:
        print("OK")


def createtable_in_host_rate(table_create_sql):

    db =get_create_host_visitdb()

    if db is None:
        logging.info('createtable_in_host_rate fail')
        return
    try:
        db.execute(table_create_sql)

    except MySQLdb.Error,e:
        if e.args[0]!=1050:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    else:
        print("OK")

def create_url_check_detail_furture():

    next_15day_table_names=[]


    timeNow = datetime.datetime.now()
    for d in range(0,15):
        anotherTime = timeNow + datetime.timedelta(days=d)
        next_15day_table_names.append(anotherTime)


    for day in next_15day_table_names:
        tbl_name = 'z_'+day.strftime('%Y_%m_%d')
        tmp = '''CREATE TABLE {0} (
          Id bigint(21) NOT NULL auto_increment,
          host_name bigint(32),
          host_visit_count bigint(32),
          check_date DATETIME,
          PRIMARY KEY  (Id)
        ) ENGINE=InnoDB, character set = utf8;;
        '''.format(tbl_name)
        createtable_in_host_rate(tmp)

def get_today_host_visit_tblname():
    timeNow = datetime.datetime.now()
    tbl_name = 'z_' + timeNow.strftime('%Y_%m_%d')
    return  tbl_name


def createalltables():
    createtable(forgeurls)
    createtable(redirecturlrules)
    createtable(url_check_stat)
    create_url_check_detail_furture()

createalltables()

if __name__ == '__main__':

    createalltables()
    print get_today_host_visit_tblname()
