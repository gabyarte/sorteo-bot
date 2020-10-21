from telegram.ext import CommandHandler

from src.db.models import User


def start(update, context):
    user_id = update.message.from_user
    User.documents.insert({'telegram_id': user_id, 'is_admin': False, 'is_blocked': False})


start_handler = CommandHandler('start', start)
