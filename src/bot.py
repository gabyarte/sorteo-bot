import logging

from telegram.ext import Updater

from src.settings import *

# handlers
from src.commands.start import start_handler
from src.commands.create_raffle import create_raffle_handler
from src.commands.participate import participate_raffle_handler
from src.commands.list_my_raffles import my_raffles_handler
from src.commands.list_all_raffles import all_raffles_handler
from src.commands.raffle_query_flow import raffle_callback_query_handler
from src.commands.list_block_users import list_blocked_handler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

class RaffleBot:
    def run(self):
        updater = Updater(TOKEN, use_context=True)

        dp = updater.dispatcher
        dp.add_handler(start_handler)
        dp.add_handler(create_raffle_handler)
        dp.add_handler(participate_raffle_handler)
        dp.add_handler(raffle_callback_query_handler)
        dp.add_handler(my_raffles_handler)
        dp.add_handler(all_raffles_handler)
        dp.add_handler(list_blocked_handler)


        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook(APP_NAME + TOKEN)
        updater.idle()
