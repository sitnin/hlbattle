#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locale, sys
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import config
import tornado.httpserver
import tornado.ioloop
import tornado.web
from redis import Redis
from urllib import unquote
from pprint import pformat
import string
from operator import itemgetter


class Posts(tornado.web.RequestHandler):
    def get(self, page=None):
        """ render posts list page (10 by page) """
        if page is None:
            page = 1
        else:
            page = int(page)
        if page < 1:
            raise tornado.web.HTTPError(404)
        offset = (page - 1) * 10
        self.write("Hello, world!")

    def post(self):
        def map(text):
            res = list()
            for line in text.splitlines():
                line = line.strip()
                words = line.split()
                for word in words:
                    res.append([unicode(word.strip(string.punctuation+string.whitespace+"«»…".decode("utf-8")).lower()), 1])
            return res

        def reduce(mapped_words, post_id):
            word2count = {}
            for word, count in mapped_words:
                if len(word) > 2:
                    try:
                        word2count[word] = word2count.get(word, 0) + count
                    except ValueError:
                        pass
 
            sorted_word2count = sorted(word2count.items(), key=itemgetter(0))
            for word, count in sorted_word2count:
                key = "idx:posts:%s"%word
                l = R.llen(key)
                idx = R.lrange(key, 0, l-1)
                if not post_id in idx:
                    R.rpush(key, post_id)

        """ save new post """
        title = self.get_argument("title")
        body = self.get_argument("body")
        tags = self.get_argument("tags")

        while True:
            try:
                post_id = R.incr("last_post_id")
                if not post_id:
                    raise Exception("not an ID")
                break
            except Exception, e:
                pass
        
        R.set("post:%d:title"%post_id, title)
        R.set("post:%d:body"%post_id, body)
        R.set("post:%d:tags"%post_id, tags)
        reduce(map(title+" "+body), post_id)
        self.write(str(post_id))
        # self.redirect("")


class OnePost(tornado.web.RequestHandler):
    def get(self, id):
        """ render one post with comments tree"""
        raise NotImplementedYet()


class Tags(tornado.web.RequestHandler):
    def get(self, id):
        """ render tag cloud """
        raise NotImplementedYet()


class OneTag(tornado.web.RequestHandler):
    def get(self, id):
        """ render posts list by tag """
        raise NotImplementedYet()


class Search(tornado.web.RequestHandler):
    def get(self, expression):
        """ render search results """
        unquoted = unquote(expression)
        raise NotImplementedYet()


class PostComments(tornado.web.RequestHandler):
    def post(self, id):
        """ save post comment """
        body = self.get_argument("body")
        parent_id = self.get_argument("parent_id", None)
        self.redirect("/posts/%d"%id)
        raise NotImplementedYet()


class NotImplementedYet(Exception):
    pass


application = tornado.web.Application([
    ("/posts", Posts),
    ("/", Posts),
    (r"/posts/page/([0-9]+)", Posts),
    (r"/posts/([0-9]+)", OnePost),
    (r"/posts/([0-9]+)/comments", PostComments),
    (r"/tags", Tags),
    (r"/tags/([0-9]+)", OneTag),
    (r"/search/(.+)", Search),
], debug=config.debug, template_path=os.path.join(os.path.dirname(__file__), 'templates'))


if __name__ == "__main__":
    R = Redis(config.db_host)
    R.select(config.db_idx)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.bind(config.port, config.host)
    http_server.start(0)
    tornado.ioloop.IOLoop.instance().start()
