from telegram.ext import CommandHandler

from src.db.models import User
from src.utils.utils import list_raffles
from src.utils.emojis import PENSIVE, WINK, GRIMACING
from src.utils.markups import CANCEL_MARKUP


def start(update, context):
    user_id = update.message.from_user.id
    user = User.documents.get(user_id, 'telegram_id')
    if user.is_block:
        update.message.reply_text(f'Tu usuario ha sido bloqueado por los administradores {GRIMACING}')
    else:
        raffles = user.get_raffles()

        if raffles:
            list_raffles(raffles, 'Tus sorteos:', user_id, update, cancel=CANCEL_MARKUP)
        else:
            update.message.reply_text(f'No tienes ningún sorteo {PENSIVE}. Para participar pon el comando /participar {WINK}.')


my_raffles_handler = CommandHandler('mis_sorteos', start)