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

def record_block_url(data):

    try:
        visit_time = time.strftime('%Y-%m-%d %H:%M:%S')
        data = decode_msg = base64.b64decode(data)
        block_info = data.split("||")
        logging.warn('record_block_url {}', str(block_info))
        block_type = block_info[0]
        block_url = block_info[1]
        dbobj, conn = getDbOrCreatex()
        dbobj.execute("insert into redirect_history (reason,fullurll,visit_time)  values(%s,%s,%s)", (block_type, block_url, visit_time))
        conn.commit()

    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())


def clean_onexit():
    print 'exit ',sys.argv
    os._exit(1)

def listen_exit(name):
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
    while 1:
            rdata = socket.recv()
            cache_info[idx] = rdata
            if str(rdata).startswith("block"):
                record_block_url(rdata[5:])
                continue
            idx=idx+1
            if idx ==max_count:
                idx=0
                pipe = obj.pipeline()
                pipe.rpush('visitinginfo', *cache_info)
                logging.info('pip.execute() result:%s, os.getpid():%s', len(pipe.execute()),os.getpid())

if len(sys.argv)<=1:
    print 'pars fail'
    start_listen_exit()
    time.sleep(111)
else:
    mylogging.setuplog('mqpuller'+str(os.getpid())+'.txt')
    create_db("redirect_history")
    max_count =1000
    if len(sys.argv)==3:
        max_count = int(sys.argv[2])
    start_listen_exit()
    listen(sys.argv[1])