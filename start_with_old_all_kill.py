# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json


import mylogging
import os
import save_log_redis
import basedef
import gpconf
cmdlines = [
    '''pkill -f 'python save_log_redis.py' ''',
    '''pkill -f 'python guideprotect.py' ''',
    '''pkill -f 'python new_url_updator.py' ''',
    '''pkill -f 'python check404.py' ''',
    '''pkill -f 'python gp_mq_puller.py zmqp1' ''',

    'python guideprotect.py'

            ]
gpconf.make_gcs()
basedef.GCS.init()
obj = save_log_redis.SaveLogging2Redis()
obj.init()
obj.save2pub({'_dtype':999})

for cmdline in cmdlines:
    os.system(cmdline)

