# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json


import mylogging
import os
import save_log_redis
import basedef
import gpconf
import redis
import time
cmdlines = [
    'python guideprotect.py'
            ]
gpconf.make_gcs()
basedef.GCS.init()
obj = save_log_redis.SaveLogging2Redis()
obj.init()
obj.save2pub({'_dtype':999})
obj = redis.Redis()
obj.publish("exitpygp", "ok")
time.sleep(1)

def start(name):
    for cmdline in cmdlines:
        os.system(cmdline)

def start_gp():
    import thread
    try:
        thread.start_new_thread(start, ('start_gp',))
    except:
        print "Error: unable to start start_listen_exit"

start_gp()


