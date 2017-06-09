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


if __name__ == '__main__':

    obj = getDbOrCreate()

    try:
        if obj is not None:
            x = obj.execute('DROP DATABASE '+DATABASE_NAME)
            print x
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())



    obj = getDbOrCreate('host_visit_rate')

    try:
        if obj is not None:
            x = obj.execute('DROP DATABASE host_visit_rate')

    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())



