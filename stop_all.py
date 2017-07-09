# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json


import mylogging
import os
cmdlines = ['''kill -s $(pidof 'python save_log_redis.py')''',
            '''kill -s $(pidof 'python new_url_updator.py')''',
            '''kill -s 9 $(pidof 'python new_url_updator.py')''',
            '''kill -s 9 $(pidof 'python save_log_redis.py')'''
            '''kill -s  $(pidof 'python guideprotect.py')'''
            '''kill -s 9 $(pidof 'python guideprotect.py')'''
            ]
for cmdline in cmdlines:
    os.system(cmdline)
