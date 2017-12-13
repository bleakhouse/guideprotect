# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging
import basedef
import redis
import traceback
from basedef import *
import os
import MySQLdb
import datetime
import gpwarning
import http_query
import gputils
import mylogging

import web
import http_query


def do_update_internal(unknow_urls):

    robj = gputils.get_black_redis()
    pipobj = robj.pipeline()

    queryobj = http_query.HttpQuery()
    queryobj.init()
    updating_url_infos={}

    for host in unknow_urls:
        if host is None:
            continue

        pipobj.hmget(host,
                     ['urltype', 'eviltype', 'evilclass', 'urlclass', 'urlsubclass', 'redirect_type', 'redirect_target',
                      'update_time'
                      ])
    res = pipobj.execute()

    counter = 0
    for host in unknow_urls:
        if host is None:
            continue


        cache = res[counter]
        counter = counter + 1

        url_info = None
        found_in_cache = None
        if cache is None or len(cache) == 0:
            trytimes = 10
            while trytimes > 0:
                url_info = queryobj.http_check_url_type(host)
                if url_info != 1:
                    break
                trytimes = trytimes - 1
                if trytimes == 0:
                    logging.warning('exceed try times!!')

            if url_info is None or url_info == 1:
                continue
        else:
            # in cache
            continue



        url_type = url_info[0]

        if int(url_type)==0 or int(url_type)==1:
            #still unknow
            continue

        # unknow to know

        urlinfo = {}
        urlinfo['urltype'] = url_type
        urlinfo['eviltype'] = url_info[1]
        urlinfo['evilclass'] = url_info[2]
        urlinfo['redirect_type'] = 'file'
        urlinfo['redirect_target'] = 'safe_navigate.html'
        urlinfo['urlclass'] = url_info[3]
        urlinfo['urlsubclass'] = url_info[4]
        urlinfo['update_time'] = int(time.time())
        urlinfo['info_src'] = 'tx_online_query'

        updating_url_infos[host] = urlinfo

    if len(updating_url_infos) > 0:
        pip = robj.pipeline()
        unknowobj = gputils.get_unknow_redis()

        erase_host=[]
        for host, update_info in updating_url_infos.items():
            pip.hmset(host, update_info)
            erase_host.append(host)
        #erase from unknow set
        unknowobj.srem(gputils.get_unknow_redis_keyname(),*erase_host)

        lenexec = pip.execute()
        if gputils.show_noisy_logging():
            logging.info('url updator pip.execute():%s', len(lenexec))

def do_update(name, unknow_urls):

    while len(unknow_urls):
        hosts = unknow_urls[:50]
        unknow_urls = unknow_urls[50:]
        do_update_internal(hosts)

class run_url_updator(object):
    def Start(self, unknow_list, name='do_update-1'):
        try:
            name = time.strftime('updatethread %Y-%m-%d %H:%M:%S')
            thread.start_new_thread(do_update, (name,unknow_list))
        except:
            print "Error: unable to start run_url_updator"


def clean_onexit():
    print 'exit ', sys.argv
    logging.info('star saving redis......:%s', str(sys.argv))
    gputils.get_black_redis().save()
    gputils.get_unknow_redis().save()
    logging.info('end saving redis..!')

    os._exit(1)

def handle_cmd(data):
    if gputils.is_cmd_go_die(data):
        clean_onexit()
        return
    msg  =gputils.extra_cmd_msg(data)
    if msg.startswith('noisy_'):
        gputils.set_noisy_logging(msg)

    # if msg == 'new_updator':
    #     name = time.strftime('%Y-%m-%d %H:%M:%S')
    #     logging.info("start updator %s", name)
    #     name = 'newupdator' + str(name)
    #     run_url_updator().Start(name)

if __name__ == '__main__':
    mylogging.setuplog('url_unknown_checker.txt')
    gputils.start_listen_cmd(handle_cmd)
    obj = gputils.get_unknow_redis()
    last_list =None
    slice_step = 50
    conthread = 5
    while 1:
        all_unknown = obj.smembers(gputils.get_unknow_redis_keyname())
        all_unknown = list(all_unknown)
        if last_list is not None and  last_list is not  None and  abs(len(last_list)-len(all_unknown))<100:
            logging.info('wait')
            time.sleep(3600*10) #after ten hours
            continue
        if len(all_unknown):
            last_list = all_unknown

            slice_step = len(all_unknown)/conthread
            logging.info('unknow check slice_step:%s', slice_step)

            for i in range(0,len(all_unknown), slice_step):
                part = all_unknown[i:i+slice_step]
                run_url_updator().Start(part)
        nexttime = len(all_unknown)+10*60
        logging.info('wait nexttime:%s', nexttime)
        time.sleep(nexttime)   #10 mins