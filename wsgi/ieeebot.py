# IEEEbot
# Copyright (C) 2015 Rafael Bailón-Ruiz <rafaelbailon@ieee.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
DATABASE_FILE = os.path.join(os.environ['OPENSHIFT_DATA_DIR'],'database.sqlite')

# Load token from environment variable 'IEEEBOT_TOKEN'.
TOKEN = os.environ['IEEEBOT_TOKEN']

# Create a database object to store points
storage = Storage(DATABASE_FILE)

# Check if database existe, if not create it
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
logger.setLevel(logging.DEBUG)  # or use logging.INFO
ch.setFormatter(formatter)

# Keep last update timestamp
last_update_id = 0


def process_update(update):
    message = telebot.types.Message.de_json(update['message'])
    bot.process_new_messages([message])


def get_karma_ranking_message():
    logger.debug("entra get_karma_ranking_message")
    text = "📊 Ranking actual:\n\n"

    karma_ranking = storage.ranking

    if karma_ranking:
        for entry in karma_ranking:
            text += "‣ {0}: {1} puntos\n".format(entry[0], entry[1])
        logger.debug("sale get_karma_ranking_message")
        return text


@bot.message_handler(commands=['ranking'])
def ranking_handler(message):
    """
    Send karma ranking
    """
    logger.debug("entra ranking_handler")
    bot.reply_to(message, get_karma_ranking_message())
    logger.debug("sale ranking_handler")


def update_karma(user_name, points):
    # No more than 5 points
    if user_name != 'aroldan':
        points = MAX_POINTS if points > MAX_POINTS else points
        points = -MAX_POINTS if points < -MAX_POINTS else points

    # SQL query will add points and insert a new user if it does not exist.
    # It will returns the final karma points too.
    return storage.update_user_karma(user_name, points)


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

        # Don't allow karma changes in private conversations
        if not isinstance(message.chat, telebot.types.GroupChat):
            bot.reply_to(message, "Nada de subir karma por lo bajini ¿eh? 😒")
            return

        # One cannot give karma to itself
        if message.from_user.username == user_name:
            bot.reply_to(message, "Ni lo intentes... 😒")
            return

        karma = update_karma(user_name, points)
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
        
        # Don't allow karma changes in private conversations
        if not isinstance(message.chat, telebot.types.GroupChat):
            bot.reply_to(message, "Las humillaciones sólo en público, por favor 😈")
            return

        # One cannot give karma to itself
        if message.from_user.username == user_name:
            bot.reply_to(message, "Tontos hay en todos lados 😆")
            return

        karma = update_karma(user_name, points)
        bot.reply_to(message,
                     "El karma de {0} ha bajado a {1} 👎\n"
                     .format(user_name, karma))

if __name__ == '__main__':
    # Use none_stop flag to not stop when get new message occur error.
    # Interval setup. Sleep 3 secs between request new message.
    bot.polling(none_stop=True, interval=3)
    bot.polling_thread.join()
