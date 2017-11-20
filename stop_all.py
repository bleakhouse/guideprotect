# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import redis
import time
import mylogging
import os

obj = redis.Redis()
obj.publish("exitpygp", "ok")
time.sleep(1)