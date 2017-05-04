# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging

import os

def check(ginfo):
    if 'redirect_count' in ginfo.keys():
        print 'redirect_count:',ginfo['redirect_count']
