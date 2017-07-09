# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json


import mylogging
import os
cmdlines = [
    '''pkill -f 'python save_log_redis.py' ''',
    '''pkill -f 'python guideprotect.py' ''',
    '''pkill -f 'python new_url_updator.py' ''',
    'python guideprotect.py'

            ]
for cmdline in cmdlines:
    os.system(cmdline)

