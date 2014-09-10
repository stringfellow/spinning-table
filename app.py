#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import momoko
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.httpserver

from tornado.options import options, define

define("port", default=8888, help="run on the given port", type=int)
define("host", default='0.0.0.0', help="run on the given inet", type=str)

db_database = os.environ.get('SPINNING_DB', '')
db_user = os.environ.get('SPINNING_USER', 'postgres')
db_password = os.environ.get('SPINNING_PASSWORD', '')
db_host = os.environ.get('SPINNING_HOST', '')
db_port = os.environ.get('SPINNING_PORT', 5432)
enable_hstore = True if os.environ.get(
    'SPINNING_HSTORE', False) == '1' else False
dsn = 'dbname=%s user=%s password=%s host=%s port=%s' % (
    db_database, db_user, db_password, db_host, db_port)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", Main),
            (r"/websocket/", QueryTable),
        ]
        settings = dict(
            static_path=os.path.join(os.path.abspath('.'), 'templates')
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = momoko.Pool(
            dsn=dsn,
            size=1,
            max_size=3,
            setsession=("SET TIME ZONE UTC",),
            raise_connect_errors=False,
        )


class DbMixin(object):
    @property
    def db(self):
        return self.application.db


class QueryTable(tornado.websocket.WebSocketHandler, DbMixin):
    def open(self):
        pass
        # clients.append(self)

    def on_message(self, message):
        pass

    def on_close(self):
        pass
        # clients.remove(self)


class Main(tornado.web.RequestHandler, DbMixin):
    def get(self):
        self.render("querytable.html")


def main():
    tornado.options.parse_command_line()
    httpserver = tornado.httpserver.HTTPServer(Application())
    httpserver.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
