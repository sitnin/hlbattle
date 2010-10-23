#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale, sys
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import fnmatch
import random


def load_data(path):
    data = list()
    for filename in fnmatch.filter(os.listdir(path), "*.txt"):
        with open(path+"/"+filename, "r") as f:
            lines = f.read().splitlines()
            f.close()
        data.append((lines[0], lines[1:]))
    return data

def run(count, data):
    def get_content(item):
        text = ""
        title = item[0]
        for s in item[1]:
            text += s+"\n"
        return (title, text)

    for x in xrange(count):
        
    
    for item in data:
        print(get_content(item))
    
def print_result(res):
    pass


if __name__ == "__main__":
    print_result(run(100, load_data("data/")))
