__author__ = 'Administrator'
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import platform
import ConfigParser
import basedef
import os
import logging
import traceback


class Warning(object):
    warning_email_on =0
    send_list=[]
    section_name='warning'

    def init(self):
        cfg = basedef.GCFG
        cfgobj = ConfigParser.ConfigParser()
        if not os.path.isfile(cfg):
            return

        try:
            cfgobj.read(cfg)
            if cfgobj.has_option(self.section_name, 'emailto'):
                warning_email = cfgobj.get(self.section_name,'emailto')
                self.send_list = warning_email.strip().split(';')


            if cfgobj.has_option(self.section_name, 'warning_on'):
                self.warning_email_on = cfgobj.getint(self.section_name, 'warning_on')
            logging.info('warning_email_on:%s', self.warning_email_on)
            for send in self.send_list:
                logging.info('send warning email:%s', send)

        except Exception, e:
            logging.error(str(e))
            logging.error(traceback.format_exc())


    def sendmail(self,warning, subj="exception occur."):

        if self.warning_email_on==0:
            return
        pl = platform.platform()
        if pl.startswith("Windows") is False:
            for send in self.send_list:
                msg = MIMEText(str(warning))
                msg["From"] = "guide protect"
                msg["To"] = send
                msg["Subject"] = str(subj)
                p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
                p.communicate(msg.as_string())


