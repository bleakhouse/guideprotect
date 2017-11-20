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

for cmdline in cmdlines:
    os.system(cmdline)

