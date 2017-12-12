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
    obj.publish("common_cmd", sys.argv[1])
    time.sleep(1)
