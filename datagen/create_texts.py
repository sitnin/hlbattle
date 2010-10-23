#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale, sys
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import random
import urllib
from BeautifulSoup import BeautifulSoup


count = 100
base_url = "http://vesna.yandex.ru/all.xml"
themes = (
    "astronomy","geology","gyroscope","literature","marketing",
    "mathematics","music","polit","agrobiologia","law","psychology",
    "geography","physics","philosophy","chemistry","estetica"
)


if __name__ == "__main__":
    themes_count = len(themes)
    for x in xrange(count):
        filename = "%s.txt"%str(x).rjust(4, "0")
        theme = random.randint(0, themes_count-1)
        url = base_url + "?mix=%s&%s=on"%(themes[theme], themes[theme])
        print "Fetching %s"%url
        data = urllib.urlretrieve(url)
        with open(data[0], "r") as f:
            utf8_data = f.read().decode("cp1251").encode("utf8")
            f.close()
        soup = BeautifulSoup(''.join(utf8_data))
        with open("data/%s"%filename, "w") as f:
            f.write(soup.find("h1").string[7:-1]+"\n")
            for p in soup.findAll("p"):
                f.write(p.string+"\n")
            f.close()
        print "Saved to %s"%filename
