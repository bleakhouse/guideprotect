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
DATABASE_NAME  = 'guideprotect'

def getDbOrCreate(dbname=DATABASE_NAME):

    obj=None
    op = None
    try:

        obj = MySQLdb.connect("127.0.0.1","test","123456",  charset="utf8")

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
  {1} varchar(128) NOT NULL default '',
  {2} varchar(128) NOT NULL default '',
  {3} varchar(128) NOT NULL default '',
  {4} varchar(1024) NOT NULL default '',
  {5} varchar(1024) NOT NULL default '',
  AddTime timestamp default CURRENT_TIMESTAMP,
  PRIMARY KEY  (Id)
) ENGINE=InnoDB, character set = utf8;;
'''.format(basedef.RULE_ATTR_NAME_name, basedef.RULE_ATTR_NAME_host, basedef.RULE_ATTR_NAME_redirect_type, basedef.RULE_ATTR_NAME_req,
           basedef.RULE_ATTR_NAME_redirect_target, basedef.RULE_ATTR_NAME_req_match_method)



def createtable(name):

    db =getDbOrCreate(DATABASE_NAME)

    if db is None:
        logging.info('getDbOrCreate fail')
        return
    try:
        db.execute(name)

    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    else:
        print("OK")

def createalltables():
    createtable(forgeurls)
    createtable(redirecturlrules)

createalltables()
if __name__ == '__main__':
    createalltables()