# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging

import os
import datetime
from dbase import db


def check(ginfo):

    if 'redirect_count' in ginfo.keys():
        print 'redirect_count:',ginfo['redirect_count']




#from dbase import db
#db.create_url_check_detail_furture()