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
        self.sql.execute('create table karma ' +
                         '(username text unique, karma integer)')

    def get_user_karma(self, username):
        t = (username,)
        result = self.sql.select('select karma from karma where username=?', t)
        try:
            return next(result)[0]  # return karma value
        except StopIteration:
            return None

    def update_user_karma(self, username, points):
        result = self.sql.select(
            ('INSERT OR REPLACE INTO karma (username, karma) VALUES(?,' +
             'COALESCE((SELECT karma FROM karma WHERE username = ?), 0) + ?);',
             'SELECT karma FROM karma WHERE username = ?;'),
            ((username, username, points), (username,)))

        try:
            return next(result)[0]  # return karma value
        except StopIteration:
            return None

    @property
    def ranking(self):
        return list(self.sql.select('select * from karma order by karma desc'))

    def close(self):
        sql.close()

if __name__ == '__main__':
    storage = Storage('database.sqlite')
