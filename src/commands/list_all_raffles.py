from telegram.ext import CommandHandler

from src.db.models import Raffle, User
from src.utils.markups import CANCEL_MARKUP
from src.utils.utils import list_raffles

def start(update, context):
    user_id = update.message.from_user.id
    user = User.documents.get(user_id, 'telegram_id')

    if user.is_admin:
        raffles = Raffle.documents.all()
        list_raffles(raffles, 'Lista de todos los sorteos:', user_id, update, cancel=CANCEL_MARKUP)


all_raffles_handler = CommandHandler('sorteos', start)
