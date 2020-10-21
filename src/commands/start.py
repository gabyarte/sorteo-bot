from telegram.ext import CommandHandler

from src.db.models import User


def start(update, context):
    user_id = update.message.from_user.id
    User.documents.insert({'telegram_id': user_id, 'is_admin': False, 'is_blocked': False})

    update.message.reply_text(f'Hola {update.message.from_user.name}')


start_handler = CommandHandler('start', start)
