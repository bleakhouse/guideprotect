import os
import zmq
import random
import sys
import time
import logging
import logging.handlers
import mylogging
import redis
import MySQLdb
import os
import traceback
import base64
import gputils

def getDbOrCreatex(dbname='guideprotect'):
    conn=None
    op = None
    try:

        MYSQL_HOST = "127.0.0.1"
        MYSQL_USR = 'test'
        MYSQL_PWD = '123456'
        conn = MySQLdb.connect(MYSQL_HOST,MYSQL_USR,MYSQL_PWD,  charset="utf8")

        op = conn.cursor()
        op.execute("CREATE DATABASE if not exists {0} DEFAULT CHARACTER SET 'utf8'".format(dbname))
        op.execute("use "+dbname)
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
    return  op, conn

def create_db(tbl_name):
    table_create_sql = '''CREATE TABLE {0} (
      Id bigint(21) NOT NULL auto_increment,
      reason bigint(32) default 0, 
      fullurll varchar(1024) NOT NULL default '',
      visit_time DATETIME  ,
      PRIMARY KEY  (Id)
    ) ENGINE=InnoDB, character set = utf8;;
    '''.format(tbl_name)
    dbobj, conn = getDbOrCreatex()
    if dbobj is None:
        logging.info('createtable_in_ fail ', tbl_name)
        return
    try:
        dbobj.execute(table_create_sql)

    except MySQLdb.Error,e:
        if e.args[0]!=1050:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    else:
        print("OK!")
        logging.warn("create table %s ok!!", tbl_name)
import time
lasttime=0
def record_block_url(sqlobj,data):

    try:
        visit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        data = decode_msg = base64.b64decode(data)
        block_info = data.split("||")

        block_type = block_info[0]
        block_url = block_info[1]
        dbobj=sqlobj[0]
        conn=sqlobj[1]
        global lasttime
        if time.time()-lasttime>60*10 or dbobj is None:
            lasttime = time.time()
            dbobj, conn = getDbOrCreatex()
            sqlobj[0]= dbobj
            sqlobj[1] = conn
        if dbobj:
            if gputils.show_noisy_logging():
                logging.warn('record_block_url %s', str(block_info))
            dbobj.execute("insert into redirect_history (reason,fullurll,visit_time)  values(%s,%s,%s)", (block_type, block_url, visit_time))
            conn.commit()

    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
        sqlobj[0] = None
        sqlobj[1] = None

def clean_onexit():
    print 'exit ',sys.argv
    os._exit(1)

def handle_cmd(data):
    if gputils.is_cmd_go_die(data):
        clean_onexit()
        return
    msg  =gputils.extra_cmd_msg(data)
    if msg.startswith('noisy_'):
        gputils.set_noisy_logging(msg)

def listen(pipname, max_count=1000):
    context = zmq.Context()
    pipid = sys.argv[1]
    socket = context.socket(zmq.PULL)
    bindaddr = "ipc:///tmp/guideprotect.mq."+pipname
    print bindaddr
    socket.connect(bindaddr)

    obj = redis.Redis()
    cache_info =range(max_count)
    idx =0
    dbobj, conn = getDbOrCreatex()
    sqlobj=[]
    sqlobj.append(dbobj)
    sqlobj.append(conn)

    while 1:
            rdata = socket.recv()

            if str(rdata).startswith("block"):
                record_block_url(sqlobj, rdata[5:])
                continue
            cache_info[idx] = rdata
            idx=idx+1
            if idx ==max_count:
                idx=0
                pipe = obj.pipeline()
                pipe.rpush('visitinginfo', *cache_info)
                lenexec = len(pipe.execute())
                if gputils.show_noisy_logging():
                    logging.info('pip.execute() result:%s, os.getpid():%s', lenexec,os.getpid())
import gpconf
import basedef
import gpwarning

if len(sys.argv)<=1:
    print 'pars fail'
else:
    mylogging.setuplog('mqpuller'+str(os.getpid())+'.txt')
    create_db("redirect_history")
    gpconf.make_gcs()
    basedef.GCS.init()
    basedef.GWARNING =gpwarning.Warning()
    basedef.GWARNING.init()

    max_count =1000
    if len(sys.argv)==3:
        max_count = int(sys.argv[2])
    gputils.start_listen_cmd(handle_cmd)
    listen(sys.argv[1])