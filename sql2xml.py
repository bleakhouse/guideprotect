# -*- coding: UTF-8 -*-
__author__ = 'Administrator'
import json
import logging
import logging.handlers
import platform
import thread
import time
import urllib2
import netifaces as netif
import platform
from basedef import *
import os
import traceback



try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET




from dbase import db


FILE_URL_RULES_NAME   = ('url_rule.xml')


def pretty_xmlfile(fname):
    from lxml import etree as ET
    parser = ET.XMLParser(
        remove_blank_text=False, resolve_entities=True, strip_cdata=True)
    xmlfile = ET.parse(fname, parser)
    pretty_xml = ET.tostring(
        xmlfile, encoding = 'UTF-8', xml_declaration = True, pretty_print = True)
    file = open(fname, "w")
    file.writelines(pretty_xml)
    file.close()

def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i


def dumpsql2xml(fname=FILE_URL_RULES_NAME):

    if os.path.isfile(fname):
        inp = raw_input('file {0} existed, ok to overwrite ? press 1 to continue\n'.format(fname))

        if not inp.isdigit():
            return

        if (int)(inp) != 1:
            return


    dbobj = db.getDbOrCreate()
    number = dbobj.execute('select * from redirecturlrules')
    if number==0:
        print 'there is no records in database'
        return
    result = dbobj.fetchall()

    rule={}

    doc = ET.Element('doc')
    doc.attrib['version'] = '1.0'

    for row in result:
        rule[RULE_ATTR_NAME_name] = row[1]
        rule[RULE_ATTR_NAME_host] = row[2]
        rule[RULE_ATTR_NAME_redirect_type] = row[3]
        rule[RULE_ATTR_NAME_req] = row[4]
        rule[RULE_ATTR_NAME_redirect_target] = row[5]
        rule[RULE_ATTR_NAME_req_match_method] = row[6]
        rule[RULE_ATTR_NAME_full_url] = row[7]


        rulenode = ET.SubElement(doc,RULE_ATTR_NAME_rule)
        rulenode.attrib[RULE_ATTR_NAME_name] = rule[RULE_ATTR_NAME_name]

        host            = ET.SubElement(rulenode, RULE_ATTR_NAME_host)
        redirect_type   = ET.SubElement(rulenode, RULE_ATTR_NAME_redirect_type)
        req             = ET.SubElement(rulenode, RULE_ATTR_NAME_req)
        redirect_target = ET.SubElement(rulenode, RULE_ATTR_NAME_redirect_target)
        req_match_method = ET.SubElement(rulenode, RULE_ATTR_NAME_req_match_method)
        full_url = ET.SubElement(rulenode, RULE_ATTR_NAME_full_url)

        host.text           = rule[RULE_ATTR_NAME_host]
        redirect_type.text  = rule[RULE_ATTR_NAME_redirect_type]
        req.text            = rule[RULE_ATTR_NAME_req]
        redirect_target.text = rule[RULE_ATTR_NAME_redirect_target]
        req_match_method.text = rule[RULE_ATTR_NAME_req_match_method]
        full_url.text = rule[RULE_ATTR_NAME_full_url]

    tree = ET.ElementTree(doc)
    tree.write(fname, encoding="UTF-8")
    pretty_xmlfile(fname)
    print '\n\n'

import sys
if __name__=='__main__':
    print sys.argv
    try:
        if len(sys.argv)==2:
            dumpsql2xml(sys.argv[1])
        else:
            dumpsql2xml()
    except Exception, e:
        logging.error(str(e))
        logging.error(traceback.format_exc())

    raw_input('press anykey to exit!\n')
