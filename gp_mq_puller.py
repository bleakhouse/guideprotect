import os
import zmq
import random
import sys
import time
import logging
import logging.handlers
import mylogging
import redis


def listen(pipname):
    context = zmq.Context()
    pipid = sys.argv[1]
    print 'pipname:'+pipname
    socket = context.socket(zmq.PULL)
    bindaddr = "ipc:///guideprotect.mq."+pipname
    print bindaddr
    socket.bind(bindaddr)

    obj = redis.Redis()
    cache_info =range(1000)
    idx =0
    while 1:
            rdata = socket.recv_string()
            cache_info[idx] = rdata
            idx=idx+1
            if idx ==1000:
                idx=0
                pipe = obj.pipeline()
                pipe.rpush('visitinginfo', *cache_info)
                logging.info('pip.execute()os.getpid():%s,count:%s',os.getpid(), len(pipe.execute()))

if len(sys.argv)!=2:
    print 'pars fail'
else:
    mylogging.setuplog('mqpuller')
    listen(sys.argv[1])