#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

"""
This bot handles inline queries for dota2 hero responses
"""
from uuid import uuid4

import re
import os

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram import InlineQueryResultAudio
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
import sqlite3

import dota_wiki_parser as parser
import properties

SCRIPT_DIR = os.path.dirname(__file__)
heroes_dict = parser.dictionary_from_file("heroes.json")


# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()
    #logger.info("query: " + query)

    RESPONSES_DB_CONN = sqlite3.connect(os.path.join(SCRIPT_DIR, 'responses.db'))
    RESPONSES_DB_CURSOR = RESPONSES_DB_CONN.cursor()
    for row in RESPONSES_DB_CURSOR.execute("SELECT response, link FROM responses WHERE response LIKE ? LIMIT 50", ["%" + query + "%"]):
        short_hero_name = parser.short_hero_name_from_url(row[1])
        hero_name = heroes_dict[short_hero_name]
        #logger.info(row)
        results.append(InlineQueryResultAudio(
                id=uuid4(),
                title=row[0],
                audio_url=row[1],
                performer=hero_name))


    bot.answerInlineQuery(update.inline_query.id, results=results)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(properties.TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.addHandler(CommandHandler("start", start))
    dp.addHandler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.addHandler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.addErrorHandler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

