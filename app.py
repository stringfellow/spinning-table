#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from datetime import datetime, timedelta

import psycopg2
#import momoko
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
db_host = os.environ.get('SPINNING_HOST', '127.0.0.1')
db_port = os.environ.get('SPINNING_PORT', 5432)
enable_hstore = True if os.environ.get(
    'SPINNING_HSTORE', False) == '1' else False
dsn = 'dbname=%s user=%s host=%s port=%s' % (
    db_database, db_user, db_host, db_port)
if db_password:
    dsn += ' password=' + db_password
print dsn


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/([^/]+)/", Main),
            (r"/websocket", QueryTable),
        ]
        settings = dict(
            static_path=os.path.join(os.path.abspath('.'), 'static'),
            template_path=os.path.join(os.path.dirname('.'), "templates"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)
#        self.db = momoko.Pool(
#            dsn=dsn,
#            size=1,
#            max_size=3,
#            setsession=("SET TIME ZONE UTC",),
#            raise_connect_errors=False,
#        )
        self.db = psycopg2.connect(dsn)


class DbMixin(object):
    @property
    def db(self):
        return self.application.db

    @property
    def cursor(self):
        return self.db.cursor()


class QueryTable(tornado.websocket.WebSocketHandler, DbMixin):
    def open(self):
        self.last_time = datetime.utcnow() - timedelta(seconds=60 * 60)

    def on_message(self, message):
        new_now = datetime.utcnow()
        elapsed = new_now - self.last_time
        # TODO: check this table exists in the db
        self.cursor.execute(
            "SELECT * FROM {0} WHERE last_login >= %s".format(message),
            (self.last_time,),
        )
        try:
            self.write_message('Query results: %s<br>' % self.cursor.fetchall())
            self.last_time = new_now
        except:
            self.write_message('[]')


class Main(tornado.web.RequestHandler, DbMixin):
    def get(self, table):
        self.render("querytable.html", table=table)


def main():
    tornado.options.parse_command_line()
    httpserver = tornado.httpserver.HTTPServer(Application())
    httpserver.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
