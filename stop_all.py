# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import redis
import time
import mylogging
import os
cmdlines = [
    '''pkill -f 'python save_log_redis.py' ''',
    '''pkill -f 'python guideprotect.py' ''',
    '''pkill -f 'python new_url_updator.py 8787' '''
    '''pkill -f 'python check404.py' '''
    '''pkill -f 'python gp_mq_puller.py zmqp1' ''',
    '''pkill -f 'python guideprotect.py' '''
            ]


obj = redis.Redis()
obj.pubsub("exitpygp", "ok")
time.sleep(1)