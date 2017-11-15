# -*- coding: UTF-8 -*-

import subprocess as sub
import sys
import time
import thread
import logging

import netifaces as netif
import os
import mylogging

import gputils
import gpconf
import snifhandler
from scapy.all import *
import visit_record
import basedef
import  gpconf
import  ignoremgr
from dbase import db
import url_redis_matcher
import ConfigParser
import gpwarning
import save_log_redis
import redis
import base64

basedef.gvar['url_visit_count'] = 0
basedef.gvar['url_block_count'] = 0
basedef.gvar['host_visited'] = {}
basedef.gvar['blocked_host_visited'] = {}
basedef.gvar['calling_hotpath'] = False
basedef.gvar['ignorepostfix'] = set()
basedef.gvar['ignorehost'] = {}

def swap32(x):
    return (((x << 24) & 0xFF000000) |
            ((x <<  8) & 0x00FF0000) |
            ((x >>  8) & 0x0000FF00) |
            ((x >> 24) & 0x000000FF))

def checkmsg(msg):
    newpkt=""
    try:
        decode_msg = base64.b64decode(msg)
        httpreq = decode_msg[16:]
        ipinfo = struct.unpack('''4i''', decode_msg[0:16])
        sip = swap32(ipinfo[0])
        dip = swap32(ipinfo[1])
        sport = (ipinfo[2])
        dport = (ipinfo[3])
        newpkt = IP(src=sip, dst=dip) / TCP(sport=sport, dport=dport) / httpreq
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())
        return

    snifhandler.sniff_check_http_packet(newpkt)

def sniff_with_redis():
    ps = redis.Redis().pubsub()
    ps.subscribe('visiting')

    print ''' ps.subscribe('visiting')'''
    for item in ps.listen():
        if item['type'] != 'message':
            continue

        msg = item['data']
        print msg
        checkmsg(msg)


def newsniff(sni):
    import pcap
    import dpkt
    pc = pcap.pcap(sni, promisc=True)
    pc.setfilter('tcp dst port 80 and greater 70 and less 1000')
    for ptime, pdata in pc:
        ether = dpkt.ethernet.Ethernet(pdata)
        if ether.type != dpkt.ethernet.ETH_TYPE_IP:
                continue
        if ether.data.p!=dpkt.ip.IP_PROTO_TCP:
            continue

        try:
            snifhandler.sniff_check_http_packet(Ether(str(pdata)))
        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())


def start(sniffeth):

    logging.info('importing scapy....')

    logging.info('start sniff....%s', sniffeth)
    newsniff(sniffeth)
    #sniff_with_redis()

import basedef

import datetime

def get_time_to_flush_db():
    save_log_db_interval=None
    save_log_db_clock = None
    cfgobj = basedef.GCS.get_config_obj()
    if cfgobj is not None and cfgobj.has_option('boot', 'save_log_db_interval'):
        save_log_db_interval = cfgobj.get('boot', 'save_log_db_interval')
        hour_inter = round(int(eval(save_log_db_interval)) / 3600, 2)
        save_log_db_interval = eval(save_log_db_interval)
        logging.info('save_log_db_interval:%s', hour_inter)


    if cfgobj is not None and cfgobj.has_option('boot', 'save_log_db_clock'):
        save_log_db_clock = cfgobj.getint('boot', 'save_log_db_clock')
        logging.info('save_log_db_clock:%s', save_log_db_clock)

    return  save_log_db_interval, save_log_db_clock

def RuntimEnginThread(name):

    save_log_db_interval,save_log_db_clock = get_time_to_flush_db()
    logging.info('save_log_db_interval:%s', save_log_db_interval)
    logging.info('save_log_db_clock:%s', save_log_db_clock)
    try:
        if os.path.isfile('hotpatch.py'):
            x = __import__('hotpatch')
            x.check(basedef.gvar)
            time.sleep(3)
    except:
        logging.error("Error: RuntimEnginThread 1.1")

    if save_log_db_interval and save_log_db_clock:
        while 1:
            logging.warning('should not has 2 valid setting (save_log_db)!!!!!!!!!!!!!!!!')
            time.sleep(1)

    lasttick = 0
    while 1:
        try:
            if save_log_db_clock is not None:
                save_log_db_interval =0
                while 1:
                    time.sleep(40)
                    hour = int(time.strftime("%H", time.localtime()))
                    min = int(time.strftime("%M", time.localtime()))
                    if  min==0 and hour == save_log_db_clock and time.time()-lasttick>60:
                        lasttick = time.time()
                        logging.info('time to save visit log')
                        break
                    continue
            basedef.gcalling_hotpath = True

            if os.path.isfile('hotpatch.py'):
                #logging.info('calling hotpath')

                x = __import__('hotpatch')
                x = reload(sys.modules['hotpatch'])
                x.check(basedef.gvar)
                #logging.info('end call hotpath')

            else:
                print 'no patch file'

            r1 = visit_record.update_url_check_stat(basedef.gvar)

            r2 = visit_record.update_visit_host_rate(basedef.gvar)

            db.create_visit_furture_record()

            logging.info('start save data to mysql db')
            basedef.GSaveLogRedisPub.save2pub({'_dtype':999})

            logging.info('update_url_check_stat:%s',r1)
            logging.info('update_visit_host_rate:%s',r2)
            basedef.gcalling_hotpath = False

            if save_log_db_interval>0:
                time.sleep(save_log_db_interval)

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())
            basedef.gcalling_hotpath = False
            time.sleep(30)
            continue


class RuntimEngin(object):
    def Start(self):
        try:
            thread.start_new_thread(RuntimEnginThread, ("RuntimEnginThread-1",))
        except:
            print "Error: unable to start RuntimEnginThread"



def sub_proc(cmdline):
    logging.info('start sub proc:%s', cmdline)
    os.system(cmdline)


def start_sub_proc(tasks):
        try:
            for task in tasks:
                thread.start_new_thread(sub_proc, (task,))
        except:
            print "Error: unable to start start_sub_proc"


if __name__ == '__main__':

    mylogging.setuplog('guideprotect')
    reload(sys).setdefaultencoding("utf8")
    if len(sys.argv)>=2 and sys.argv[1].find('test')!=-1:
        basedef.GCFG = 'guideprotect - test.conf'
        logging.info('enter testing mode')

    logging.info('guideprotect up.....')

    ignoremgr.init()
    gpconf.make_gcs()
    basedef.GCS.init()
    basedef.GWARNING =gpwarning.Warning()
    basedef.GWARNING.init()

    basedef.GSaveLogRedisPub = save_log_redis.SaveLogging2Redis()
    basedef.GSaveLogRedisPub.init()

    db.createalltables()

    cmdlines = [
        '''pkill -f 'python save_log_redis.py' ''',
        '''pkill -f 'python new_url_updator.py' ''',
        '''pkill -f 'python check404.py' '''
    ]

    for cmdline in cmdlines:
        os.system(cmdline)
    cmdlines = [
                'python new_url_updator.py 8787',
                'python save_log_redis.py',
                'python check404.py',
                'python gp_mq_puller.py zmqp1',
                'python gp_mq_puller.py zmqp2',
                'python gp_mq_puller.py zmqp3',
                'python gp_mq_puller.py zmqp4',
    ]

    start_sub_proc(cmdlines)
    RuntimEngin().Start()
    #time.sleep(5)
    snife, inje= "","" #gpconf.get_sniff_eth()
    if len(snife)>0 and  len(inje)>0:
        print 'select eth:'
        print 'sniffer:',snife
        print 'inject:',inje
        snifhandler.g_redirect_eth=inje
        start(snife)
    else :
        time.sleep(2)
        sniff_with_redis()
        #logging.info('no eth selected!!')

    logging.info('guideprotect down!')
    logging.info('star saving redis......')

    r = url_redis_matcher.save_data()

    logging.info('end saving redis..!')
    print r

#p = sub.Popen(('sudo', 'tcpdump', '-w'),stdout=sub.PIPE)

