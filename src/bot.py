import logging

from telegram.ext import Updater

import settings

# handlers
from commands.create_raffle import create_raffle_handler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

class RaffleBot:
    def run(self):
        updater = Updater(settings.TOKEN, use_context=True)

        dp = updater.dispatcher
        dp.add_handler(create_raffle_handler)

        updater.start_webhook(listen="0.0.0.0",
                              port=settings.PORT,
                              url_path=settings.TOKEN)
        updater.bot.set_webhook(settings.APP_NAME + settings.TOKEN)
        updater.idle()
