# IEEEbot
# Copyright (C) 2015 Rafael Bailón-Ruiz <rafaelbailon@ieee.org>
# Copyright (C) 2015 Benito Palacios Sánchez <benito356@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3

from threading import Thread
from queue import Queue


class Storage(object):

    class MultiThreadSQLite(Thread):
        def __init__(self, db):
            super(Storage.MultiThreadSQLite, self).__init__()
            self.db = db
            self.reqs = Queue()
            self.start()

        def run(self):
            cnx = sqlite3.connect(self.db)
            cursor = cnx.cursor()
            while True:
                req, arg, res = self.reqs.get()
                if req == '--close--':
                    break

                try:
                    # If it's a tuple execute all requests
                    if type(req) is tuple:
                        for r, a in zip(req, arg):
                            cursor.execute(r, a)
                            cnx.commit()
                    else:
                        cursor.execute(req, arg)
                        cnx.commit()
                except:
                    cnx.rollback()
                if res:
                    for rec in cursor:
                        res.put(rec)
                    res.put('--no more--')
            cnx.close()

        def execute(self, req, arg=None, res=None):
            self.reqs.put((req, arg or tuple(), res))

        def select(self, req, arg=None):
            res = Queue()
            self.execute(req, arg, res)
            while True:
                rec = res.get()
                if rec == '--no more--':
                    break

                yield rec

        def close(self):
            self.execute('--close--')

    def __init__(self, database):
        self.sql = Storage.MultiThreadSQLite(database)

    def initialize(self):
        self.sql.execute('CREATE TABLE karmas (' +
                         'karma_id INTEGER  NOT NULL  PRIMARY KEY AUTOINCREMENT,' +
                         'chat_id INTEGER  NOT NULL,' +
                         'username INTEGER  NOT NULL,' +
                         'karma INTEGER NOT NULL,' +
                         'FOREIGN KEY(chat_id) REFERENCES chats(chat_id)' +
                         ')')
        self.sql.execute('CREATE TABLE chats (' +
                         'chat_id INTEGER  PRIMARY KEY NOT NULL,' +
                         'hash TEXT  NOT NULL' +
                         ')')

    def get_user_karma(self, chat_id, username):
        t = (chat_id, username)
        result = self.sql.select('select karma from karmas where chat_id=? and username=?', t)
        try:
            return next(result)[0]  # return karma value
        except StopIteration:
            return None

    def update_user_karma(self, chat_id, username, points):
        str_hash = "1234657980abcdf"
        result = self.sql.select(
            ('INSERT OR REPLACE INTO chats (chat_id, hash) VALUES(' +
             'COALESCE((SELECT chat_id FROM chats WHERE chat_id=?), ?), ?);',
             'INSERT OR REPLACE INTO karmas (karma_id, chat_id, username, karma) VALUES(?,?' +
             'COALESCE((SELECT karma FROM karmas WHERE chat_id=? AND username=?), 0) + ?);',
             'SELECT karma FROM karmas WHERE chat_id=? AND username=?;'),
            ((chat_id, chat_id, str_hash),(chat_id, username, chat_id, username, points), (chat_id, username,)))

        try:
            return next(result)[0]  # return karma value
        except StopIteration:
            return None

    def get_ranking(self, chat_id):
        print(chat_id)
        t=(chat_id,)
        result=list(self.sql.select('SELECT username, karma FROM karmas WHERE chat_id=? ORDER BY karma desc', t))
        print(result)
        return result

    def close(self):
        self.sql.close()

if __name__ == '__main__':
    storage = Storage('database.sqlite')
