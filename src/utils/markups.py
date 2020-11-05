from telegram import InlineKeyboardButton
from src.utils.emojis import CROSS


CANCEL_MARKUP = [InlineKeyboardButton(CROSS, callback_data='cancel/')]
