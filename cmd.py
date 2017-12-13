# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import redis
import time
import mylogging
import os
import sys

if len(sys.argv)!=2:
    print 'par error'
else:
    obj = redis.Redis()
    data ={'msg':sys.argv[1]}
    obj.publish("common_cmd", str(data))
    time.sleep(1)
