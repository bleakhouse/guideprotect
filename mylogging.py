# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import sys
import thread
import time
import logging
import traceback
import logging.handlers

loglist=[]

def setuplog(logname='guideprotect.txt'):

    if logname in loglist:
        return
    loglist.append(logname)

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    # create file handler
    filename=time.strftime("%Y-%m-%d", time.localtime()) +"_"+logname,

    filename= filename[0]
    fh = logging.handlers.RotatingFileHandler(filename, maxBytes=1024*1024*5, backupCount=5)
    fh.setLevel(logging.DEBUG)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

