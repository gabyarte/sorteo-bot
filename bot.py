#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from telegram.ext import Updater

from .src.commands import handlers

TOKEN = '1319297539:AAHcD1FKY77POML5NflXhlwRUDxTaeGSPV0'
APP_NAME = 'https://funny-sorteo-bot.herokuapp.com/'
PORT = int(os.environ.get('PORT', 5000))
DB_URI = "mongodb+srv://sorteoUser:XWpNDuXgj5DwEXkN@Sorteo.mongodb.net/test?retryWrites=true&w=majority"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(handlers.create_raffle_handler)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    # updater.bot.set_webhook(url=settings.WEBHOOK_URL)
    updater.bot.set_webhook(APP_NAME + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':

    main()