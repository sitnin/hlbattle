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

def map(text):
    res = list()
    for line in text.splitlines():
        line = line.strip()
        words = line.split()
        for word in words:
            res.append([unicode(word.strip(string.punctuation+string.whitespace+"«»…".decode("utf-8")).lower()), 1])
    return res

def reduce(mapped_words, index, what="posts"):
    word2count = {}
    for word, count in mapped_words:
        if len(word) > 2:
            try:
                word2count[word] = word2count.get(word, 0) + count
            except ValueError:
                pass

    sorted_word2count = sorted(word2count.items(), key=itemgetter(0))
    for word, count in sorted_word2count:
        key = "idx:%s:%s"%(word, what)
        l = R.llen(key)
        idx = R.lrange(key, 0, l-1)
        if not index in idx:
            R.rpush(key, index)


class Posts(tornado.web.RequestHandler):
    def get(self, page=None):
        """ render posts list page (10 by page) """

        def nl2br(str):
            return str.replace("\n", "<br>")

        if page is None:
            page = 1
        else:
            page = int(page)
        if page < 1:
            raise tornado.web.HTTPError(404)
        offset = (page - 1) * 10
        posts = list()
        last_id = R.get("last_post_id")
        if last_id:
            last_id = int(last_id)

            last_page = last_id/10
            if last_id%10 > 0:
                last_page += 1
            if page > last_page:
                raise tornado.web.HTTPError(404, "File Not Found")

            for x in xrange(offset, offset + 10):
                key_base = "post:%d:"%(x+1)
                title = R.get(key_base+"title")
                body = R.get(key_base+"body")
                tags = R.get(key_base+"tags")
                if title:
                    posts.append({
                        "id": x,
                        "title": title,
                        "body": body,
                        "tags": tags,
                    })
            self.render("posts.html", nl2br=nl2br, page=page, items=posts, last_page=last_page)
        else:
            self.write("There is no posts")

    def post(self):
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
        reduce(map(title+"\n"+body), post_id)
        self.redirect("/posts/%d"%post_id)


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
    def post(self, post_id):
        """ save post comment """
        body = self.get_argument("body")
        parent_id = self.get_argument("parent_id", None)

        while True:
            try:
                comment_id = R.incr("last_comment_id")
                if not post_id:
                    raise Exception("not an ID")
                break
            except Exception, e:
                pass
        
        R.set("com:%d:post"%comment_id, post_id)
        R.set("com:%d:parent"%comment_id, parent_id)
        R.set("com:%d:body"%comment_id, body)
        reduce(map(body), comment_id, "com")
        self.redirect("/posts/%d"%id)


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
