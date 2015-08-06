# IEEEbot
# Copyright (C) 2015 Rafael Bailón-Ruiz <rafaelbailon@ieee.org>
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

import json
import os

import ieeebot

from flask import Flask, request, abort
from storage import Storage

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

ieeebot.logger.debug(ieeebot.TOKEN)
ieeebot.logger.debug(ieeebot.DATABASE_FILE)


@app.route('/webhook/<token>', methods=['POST'])
def hello(token=None):
    if token == ieeebot.TOKEN:
        update = request.get_json(force=True)
        ieeebot.logger.debug(str(update))

        if update['update_id'] > ieeebot.last_update_id:
            ieeebot.last_update_id = update['update_id']
            ieeebot.process_update(update)

        return "", 200
    else:
        return "", 400

if __name__ == "__main__":
    app.run(debug=True)
