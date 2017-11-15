import os
import zmq
import random
import sys
import time

def listen(pipname):
    context = zmq.Context()
    pipid = sys.argv[1]
    print 'pipname:'+pipname
    socket = context.socket(zmq.PULL)
    #socket.setsockopt(zmq.SUBSCRIBE, 'visiting')
    bindaddr = "ipc:///guideprotect.mq."+pipname
    socket.bind(bindaddr)


    while 1:
    #       print time.time()
    #       time.sleep(0.05)
            print 'impip:',pipid,socket.recv_json().values()[0][-6:]

if len(sys.argv)!=2:
    print 'pars fail'
else:
    listen(sys.argv[1])