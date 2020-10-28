import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler

from src.db.models import Raffle, User, Number
from src.utils import show_raffle_preview, in_batches

CROSS = u"\u274C"

# TODO Add privileges check

# TODO List raffle pagination
def start(update, context):
    user_id = update.message.from_user.id

    logging.info(f'[START] user_id - {user_id}')

    raffles = Raffle.documents.find({'is_open': True})

    raffles_menu = []
    for raffle in raffles:
        raffles_menu.append([InlineKeyboardButton(f'{raffle.name} ({raffle.taken_numbers_count()}/{raffle.max_numbers})',
                                              callback_data=f'show/{raffle._id},{user_id}')])

    update.message.reply_text('Lista de sorteos disponibles:', reply_markup=InlineKeyboardMarkup(raffles_menu))


def show_handler(raffle_id, user_id, query):
    cancel_markup = [InlineKeyboardButton(CROSS, callback_data='cancel/')]
    info = None

    options_markup = []
    user = User.documents.get(user_id, key='telegram_id')
    if user.can_participate_in_another_raffle() and user.can_take_number(raffle_id):
        options_markup.append(InlineKeyboardButton('Participar', callback_data=f'get/{raffle_id},{user_id}'))
    else:
        info = 'No puede escoger número de este sorteo'

    if user.in_raffle(raffle_id):
        options_markup.append(InlineKeyboardButton('Salir', callback_data=f'out/{raffle_id},{user_id}'))

    raffle = Raffle.documents.get(raffle_id)
    if raffle:
        show_raffle_preview(raffle, query, info=info, markup=InlineKeyboardMarkup([options_markup, cancel_markup]))


def get_handler(raffle_id, user_id, query):
    raffle = Raffle.documents.get(raffle_id)
    logging.info(f'[HANDLER get] {raffle}')

    available_numbers = raffle.available_numbers()
    numbers_markup = []
    for numbers in in_batches(available_numbers, 4):
        markup = [InlineKeyboardButton(str(i), callback_data=f'choice/{raffle_id},{user_id},{i}') for i in numbers if i]
        numbers_markup.append(markup)

    query.edit_message_text('Escoge un número disponible:', reply_markup=InlineKeyboardMarkup(numbers_markup))


def choice_handler(raffle_id, user_id, number, query):
    number = Number.documents.insert({'user_id': user_id, 'raffle_id': raffle_id, 'number': number})
    query.edit_message_text(f'Felicidades! El número {number.number} dicen que es de la suerte :wink:...')


def out_handler(raffle_id, user_id, query):
    Number.documents.delete({'user_id': user_id, 'raffle_id': raffle_id})
    query.edit_message_text('Sentimos verte partir :pensive:')
    # TODO Notify admins


def cancel_handler(query):
    query.message.delete()


def callback_query_handler(update, context):
    query = update.callback_query
    query.answer()

    cmd, options = query.data.split('/')
    options = options.split(',')

    logging.info(f'[HANDLER] cmd - {cmd}\noptions - {options}')

    if cmd == 'get':
        raffle_id, user_id = options[0], int(options[1])
        logging.info(f'[HANDLER] raffle_id - {raffle_id}\nuser_id - {user_id}')
        get_handler(raffle_id, user_id, query)

    if cmd == 'show':
        raffle_id, user_id = options[0], int(options[1])
        logging.info(f'[HANDLER] raffle_id - {raffle_id}\nuser_id - {user_id}')
        show_handler(raffle_id, user_id, query)

    if cmd == 'choice':
        raffle_id, user_id, number = options[0], int(options[1]), int(options[2])
        logging.info(f'[HANDLER] raffle_id - {raffle_id}\nuser_id - {user_id}\nnumber - {number}')
        choice_handler(raffle_id, user_id, number, query)

    if cmd == 'out':
        raffle_id, user_id = options[0], int(options[1])
        logging.info(f'[HANDLER] raffle_id - {raffle_id}\nuser_id - {user_id}')
        out_handler(raffle_id, user_id, query)

    if cmd == 'cancel':
        cancel_handler(query)

list_callback_query_handler = CallbackQueryHandler(callback_query_handler)
list_raffle_handler = CommandHandler(['ver_sorteos', 'participar'], start)
