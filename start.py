# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import os
import gputils

def start_puller():
    gputils.start_sub_proc('python gp_mq_puller.py zmqp1')

def start_worker():
    gputils.start_sub_proc('python worker.py')
    gputils.start_sub_proc('python worker.py')
    gputils.start_sub_proc('python worker.py')
    gputils.start_sub_proc('python worker.py')

def start_receiver():
    gputils.start_sub_proc('python receiver.py')

def start_404():
    gputils.start_sub_proc('python receiver.py')


if __name__=='__main__':
    start_receiver()
    start_worker()
    start_puller()
    os.system('python url_unknown_checker.py')



