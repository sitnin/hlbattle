#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale, sys
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
reload(sys)
sys.setdefaultencoding('utf-8')
from operator import itemgetter
import string
import datetime 

def map():
    res = list()
    for line in sys.stdin:
        line = line.strip()
        words = line.split()
        for word in words:
            res.append([unicode(word.strip(string.punctuation+string.whitespace+"«»…".decode("utf-8")).lower()), 1])
    return res


def reduce(mapped_words):
    word2count = {}
    for word, count in mapped_words:
        if len(word) > 2:
            try:
                word2count[word] = word2count.get(word, 0) + count
            except ValueError:
                pass
 
    sorted_word2count = sorted(word2count.items(), key=itemgetter(0))
    for word, count in sorted_word2count:
        if count == 100:
            print '<div>%s<span>%s</div>'% (word, count)
    # print "----------------------------------------"
    # for word, count in sorted_word2count:
    #     print '%s\t%s'% (word, count)

start = datetime.datetime.now()
reduce(map())
end = datetime.datetime.now()
print end-start
