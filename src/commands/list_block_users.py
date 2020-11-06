from telegram.ext import CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from src.db.models import User
from src.utils.markups import CANCEL_MARKUP
from src.utils.emojis import DANGER


def start(update, context):
    user_id = update.message.from_user.id
    user = User.documents.get(user_id, 'telegram_id')

    if user.is_admin:
        blocked_users = User.documents.find({'is_blocked': True})
        list_blocked = []
        for blocked_user in blocked_users:
            chat = context.bot.get_chat(blocked_user.telegram_id)
            name = f'{chat.first_name} {chat.last_name}' if chat.first_name and chat.last_name else chat.username
            name = name if name else chat.first_name

            list_blocked.append([InlineKeyboardButton(f'{name}', callback_data=f'unblock/{blocked_user.telegram_id}')])

        update.message.reply_text(f'Bloqueados\n\n{DANGER} Si selecciones un usuario bloqueado, lo puedes *DESBLOQUEAR* y podrá participar en los sorteos disponibles', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=InlineKeyboardMarkup(list_blocked + [CANCEL_MARKUP]))


list_blocked_handler = CommandHandler('bloqueados', start)