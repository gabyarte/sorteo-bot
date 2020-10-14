import logging

from telegram.ext import Updater

from src.settings import *

# handlers
from src.commands.create_raffle import create_raffle_handler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

class RaffleBot:
    def run(self):
        updater = Updater(TOKEN, use_context=True)

        dp = updater.dispatcher
        dp.add_handler(create_raffle_handler)

        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook(APP_NAME + TOKEN)
        updater.idle()
