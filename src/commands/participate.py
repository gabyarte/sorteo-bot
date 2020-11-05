import logging
from telegram.ext import CommandHandler

from src.db.models import Raffle, User
from src.utils.utils import list_raffles
from src.utils.markups import CANCEL_MARKUP


# TODO List raffle pagination
def start(update, context):
    user_id = update.message.from_user.id

    logging.info(f'[START] user_id - {user_id}')

    user = User.documents.get(user_id, 'telegram_id')
    if not user.is_blocked:
        raffles = Raffle.documents.find({'is_open': True})

        list_raffles(raffles, 'Lista de sorteos disponibles:', user_id, update, CANCEL_MARKUP)


participate_raffle_handler = CommandHandler(['ver_sorteos', 'participar'], start)
