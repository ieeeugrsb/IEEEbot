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

import pdb

import telebot
import telebot.types
import time
import logging
import sys
import re

import os

from storage import Storage

# Regular expressions.
USERNAME_PLUS_REGEXP_SEARCH = '@([a-zA-Z0-9_]+)(\+{2,})'
USERNAME_MINUS_REGEXP_SEARCH = '@([a-zA-Z0-9_]+)(\-{2,})'
MAX_POINTS = 20

# Database file path
DATABASE_FILE = os.path.join(os.environ['OPENSHIFT_DATA_DIR'],
                             'database.sqlite')

# Load token from environment variable 'IEEEBOT_TOKEN'.
TOKEN = os.environ['IEEEBOT_TOKEN']

# Create a database object to store points
storage = Storage(DATABASE_FILE)

# Check if database exists, if not create it
if not os.path.isfile(DATABASE_FILE):
    storage.initialize()

# Create a bot
bot = telebot.TeleBot(TOKEN)

# Logging
logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(thread)d \
  {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)
logger.setLevel(logging.INFO)  # or use logging.INFO
ch.setFormatter(formatter)

# Keep last update timestamp
last_update_id = 0


def process_update(update):
    message = telebot.types.Message.de_json(update['message'])
    bot.process_new_messages([message])


def get_user_category(karma):
    '''Get classification of user depending its karma.

    Args:
        karma: user karma

    Returns:
        category: str or None
    '''
    categories = [{'range': (None, -100000), 'title': "aroldan"},
                  {'range': (-99999, -10000), 'title': "satán"},
                  {'range': (-9999, -1000), 'title': "supervillano(a)"},
                  {'range': (-999, -100), 'title': "troll"},
                  {'range': (-99, -10), 'title': "marginado(a)"},
                  {'range': (-9, -1), 'title': "chistesmalosnoplz"},
                  {'range': (0, 9), 'title': "noob"},
                  {'range': (10, 99), 'title': "wannabe"},
                  {'range': (100, 999), 'title': "sabio(a)"},
                  {'range': (1000, 9999), 'title': "elputoamo™"},
                  {'range': (10000, 100000), 'title': "dios(a)"},
                  {'range': (100000, None), 'title': "Chuck Norris"}]

    category = None

    for c in categories:
        if c['range'][0] is None:
            if karma <= c['range'][1]:
                category = c['title']
        elif c['range'][1] is None:
            if karma >= c['range'][0]:
                category = c['title']
        else:
            if karma in range(c['range'][0], c['range'][1] + 1):
                category = c['title']

    return category


def get_karma_ranking_message(chat_id):
    text = "📊 Ranking actual:\n\n"

    karma_ranking = storage.get_ranking(chat_id)
    print(karma_ranking)
    if karma_ranking:
        for entry in karma_ranking:
            # Hide users with 0 karma
            if entry[1] == 0:
                continue

            text += "‣ {0}: {1} puntos".format(entry[0], entry[1])
            category = get_user_category(entry[1])
            if category is not None:
                text += " [{0}]".format(category)
            text += "\n"

        return text


@bot.message_handler(commands=['ranking'])
def ranking_handler(message):
    """
    Send karma ranking
    """
    bot.reply_to(message, get_karma_ranking_message(message.chat.id))


def update_karma(chat_id, user_name, points):
    # No more than 5 points
    if user_name != 'aroldan':
        points = MAX_POINTS if points > MAX_POINTS else points
        points = -MAX_POINTS if points < -MAX_POINTS else points

    # SQL query will add points and insert a new user if it does not exist.
    # It will returns the final karma points too.
    return storage.update_user_karma(chat_id, user_name, points)


@bot.message_handler(regexp=USERNAME_PLUS_REGEXP_SEARCH)
def mas1_handler(message):
    """
    Increment karma
    """
    m = re.search(USERNAME_PLUS_REGEXP_SEARCH, message.text)
    if m:
        # Get user name and karma points.
        user_name = m.group(1)
        points = len(m.group(2)) - 1
        pdb.set_trace() 

#        # Don't allow karma changes in private conversations
#        if not issubclass(message.chat.__class__, telebot.types.Chat):
#            bot.reply_to(message, "Nada de subir karma por lo bajini ¿eh? 😒")
#            return

        # One cannot give karma to itself
        if message.from_user.username == user_name:
            bot.reply_to(message, "Ni lo intentes... 😒")
            return

        karma = update_karma(message.chat.id, user_name, points)
        bot.reply_to(message,
                     "El karma de {0} ha aumentado a {1} 👍\n"
                     .format(user_name, karma))


@bot.message_handler(regexp=USERNAME_MINUS_REGEXP_SEARCH)
def menos1_handler(message):
    """
    Decrement karma
    """
    m = re.match(USERNAME_MINUS_REGEXP_SEARCH, message.text)
    if m:
        # Get user name and karma points.
        user_name = m.group(1)
        points = (len(m.group(2)) - 1) * -1

#        # Don't allow karma changes in private conversations
#        if not isinstance(message.chat, telebot.types.Chat):
#            bot.reply_to(message,
#                         "Las humillaciones solo en público, por favor 😈")
#            return

        # One cannot give karma to itself
        if message.from_user.username == user_name:
            bot.reply_to(message, "Tontos hay en todos lados 😆")
            return

        karma = update_karma(message.chat.id, user_name, points)
        bot.reply_to(message,
                     "El karma de {0} ha bajado a {1} 👎\n"
                     .format(user_name, karma))


@bot.message_handler(commands=['about'])
def acercade_handler(message):
    """
    Send about text
    """
    about_text = """IEEEbot
Copyright (C) 2015 Rafael Bailón-Ruiz <rafaelbailon @ ieee . org>
Copyright (C) 2015 Benito Palacios Sánchez <benito356 @ gmail . com>

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along
with this program. If not, see <http://www.gnu.org/licenses/>.

You can get the Corresponding Source for this software from
http://github.com/ieeeugrsb/IEEEbot
"""
    bot.reply_to(message, about_text)

if __name__ == '__main__':
    # Use none_stop flag to not stop when get new message occur error.
    # Interval setup. Sleep 3 secs between request new message.
    bot.polling(none_stop=True, interval=3)
    bot.polling_thread.join()
