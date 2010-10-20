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
        self.render("posts.html", page=page, url=self.request.uri)

    def post(self):
        """ save new post """
        title = self.get_argument("title")
        body = self.get_argument("body")
        tags = self.get_argument("tags")
        raise NotImplementedYet()


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
