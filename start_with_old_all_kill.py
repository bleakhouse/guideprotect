# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json


import mylogging
import os
import save_log_redis
cmdlines = [
    '''pkill -f 'python save_log_redis.py' ''',
    '''pkill -f 'python guideprotect.py' ''',
    '''pkill -f 'python new_url_updator.py' ''',
    'python guideprotect.py'

            ]

obj = save_log_redis.SaveLogging2Redis()
obj.init()
obj.save2pub({'_dtype':999})

for cmdline in cmdlines:
    os.system(cmdline)

