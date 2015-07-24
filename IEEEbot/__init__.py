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
import time
import logging
import sys
import re

import os

TOKEN = os.environ['IEEEBOT_TOKEN']

USERNAME_PLUS_REGEXP_SEARCH = '@([a-zA-Z0-9_]+)\+\+'
USERNAME_MINUS_REGEXP_SEARCH = '@([a-zA-Z0-9_]+)\-\-'

puntos = []

bot = telebot.TeleBot(TOKEN)

### Logging
logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(thread)d {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s', '%m-%d %H:%M:%S')
ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)  # or use logging.INFO
ch.setFormatter(formatter)
###


def get_karma_ranking_message():
    logger.debug("entra get_karma_ranking_message")
    text="Ranking actual:\n\n"
    for usuario in puntos:
        text += "{0}: {1} puntos\n".format(usuario['username'], usuario['karma'])
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
    

@bot.message_handler(regexp=USERNAME_PLUS_REGEXP_SEARCH)
def mas1_handler(message):
    """
    Increment karma
    """
    m = re.search(USERNAME_PLUS_REGEXP_SEARCH, message.text)
    if m:
        logger.debug(m.group(1))
        for usuario in puntos:
            if usuario['username'] == m.group(1):
                usuario['karma'] += 1
                bot.reply_to(message, "karma +1")
                break
        else:
            puntos.append({'username':m.group(1), 'karma':1})

@bot.message_handler(regexp=USERNAME_MINUS_REGEXP_SEARCH)
def menos1_handler(message):
    """
    Decrement karma
    """
    m = re.match(USERNAME_MINUS_REGEXP_SEARCH, message.text)
    if m:
        for usuario in puntos:
            if usuario['username'] == m.group(1):
                usuario['karma'] -= 1
                bot.reply_to(message, "karma -1")
                break
        else:
            puntos.append({'username':m.group(1), 'karma':-1})

#bot.set_update_listener(listener) #register listener
bot.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
bot.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
bot.polling(interval=3)

while True: # Don't let the main Thread end.
    pass
