#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale, sys
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import sys
import fnmatch
import random
import httplib
import urllib
from pprint import pprint, pformat
import datetime

def load_data(path):
    data = list()
    for filename in fnmatch.filter(os.listdir(path), "*.txt"):
        with open(path+"/"+filename, "r") as f:
            lines = f.read().splitlines()
            f.close()
        data.append((lines[0], lines[1:]))
    return data

def run(count, data, target_host="188.127.230.23"):
    def get_content(item):
        text = ""
        title = item[0]
        for s in item[1]:
            text += s+"\n"
        tagstr = ""
        for tag in xrange(3):
            tagstr += "tag %d, "%random.randint(1, 10)
        return (title, text, tagstr[:-2])

    start = datetime.datetime.now()
    texts_count = len(data)
    log = list()
    for x in xrange(count):
        idx = random.randint(0, texts_count-1)
        title, text, tags = get_content(data[idx])
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"
        }
        params = urllib.urlencode({
            'title': title,
            'body': text,
            'tags': tags,
        })
        conn = httplib.HTTPConnection(target_host)
        conn.request("POST", "/posts", params, headers)
        response = conn.getresponse()
        resp_data = response.read()
        conn.close()
        log.append({
            "tno": idx,
            "status": response.status,
            "reason": response.reason,
            "tags": tags,
            "data": resp_data,
        })
        if x == count/10:
            print x
    end = datetime.datetime.now()
    return (start, end, log)
    
def print_result(res, logfile):
    with open(logfile, "w") as f:
        for item in res[2]:
            s = "%d %s, text no: %d, tags: %s, answer: %s\n"%(item["status"], item["reason"], item["tno"], item["tags"], item["data"])
            f.write(s)
        f.write("POSTs performed: %d\n"%len(res[2]))
        f.write("Time consumed: %s\n"%str(res[1]-res[0]))
        f.close()
    print "POSTs performed: %d"%len(res[2])
    print "Time consumed: ", res[1]-res[0]


if __name__ == "__main__":
    volume = int(sys.argv[1])
    logfile = sys.argv[2]
    print_result(run(volume, load_data("data/"), "hl.local"), logfile)
