from telegram.ext import CommandHandler

from src.db.models import User
from src.utils.utils import list_raffles
from src.utils.emojis import PENSIVE, WINK
from src.utils.markups import CANCEL_MARKUP


def start(update, context):
    user_id = update.message.from_user.id
    raffles = User.documents.get(user_id, 'telegram_id').get_raffles()

    if raffles:
        list_raffles(raffles, 'Tus sorteos:', user_id, update, cancel=CANCEL_MARKUP)
    else:
        update.message.reply_text(f'No tienes ningún sorteo {PENSIVE}. Para participar pon el comando /participar {WINK}.')


my_raffles_handler = CommandHandler('mis_sorteos', start)