import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler

from src.db.models import Raffle, User, Number
from src.utils import show_raffle_preview, in_batches

CROSS = u"\u274C"

# TODO Add privileges check

# TODO List raffle pagination
def start(update, context):
    context.user = update.message.from_user

    raffles = Raffle.documents.find({'is_open': True})

    raffles_menu = []
    for raffle in raffles:
        raffles_menu.append([InlineKeyboardButton(f'{raffle.name} ({raffle.taken_numbers_count()}/{raffle.max_numbers})',
                                              callback_data=f'show/{raffle._id}')])

    update.message.reply_text('Lista de sorteos disponibles:', reply_markup=InlineKeyboardMarkup(raffles_menu))


def show_handler(raffle_id, update, context):
    user_id = context.user.id
    cancel_markup = [InlineKeyboardButton(CROSS, callback_data='cancel')]
    info = None

    options_markup = []
    user = User.documents.get(user_id, key='telegram_id')
    if user.can_participate_in_another_raffle() and user.can_take_number(raffle_id):
        options_markup.append(InlineKeyboardButton('Participar', callback_data=f'get/{raffle_id}'))
    else:
        info = 'No puede escoger número de este sorteo'

    if user.in_raffle(raffle_id):
        options_markup.append(InlineKeyboardButton('Salir', callback_data=f'out/{raffle_id}'))

    raffle = Raffle.documents.get(raffle_id)
    show_raffle_preview(raffle, update, info=info, markup=InlineKeyboardMarkup([options_markup, cancel_markup]))


def get_handler(raffle_id, update):
    raffle = Raffle.documents.get(raffle_id)

    available_numbers = raffle.available_numbers()
    numbers_markup = []
    for numbers in in_batches(available_numbers, 3):
        markup = [InlineKeyboardButton(str(i), callback_data=f'choice/{raffle_id}/{i}') for i in numbers]
        numbers_markup.append(markup)

    update.message.reply_text('Escoge un número disponible:', reply_markup=InlineKeyboardMarkup(numbers_markup))


def choice_handler(raffle_id, number, update, context):
    user_id = context.user.id
    number = Number.documents.insert({'user_id': user_id, 'raffle_id': raffle_id, 'number': number})
    update.message.reply_text(f'Felicidades! El número {number} dicen que es de la suerte...')


def out_handler(raffle_id, update, context):
    user_id = context.user.id
    Number.documents.delete({'user_id': user_id, 'raffle_id': raffle_id})
    # TODO Notify admins


def cancel_handler(update):
    update.message.delete()


def callback_query_handler(update, context):
    query = update.callback_query
    query.answer()

    cmd, options = query.data.split('/')

    if cmd == 'get':
        raffle_id = int(options[0])
        get_handler(raffle_id, update)

    if cmd == 'show':
        raffle_id = int(options[0])
        show_handler(raffle_id, update, context)

    if cmd == 'choice':
        raffle_id, number = int(options[0]), int(options[1])
        choice_handler(raffle_id, number, update, context)

    if cmd == 'out':
        raffle_id = int(options[0])
        out_handler(raffle_id, update, context)

    if cmd == 'cancel':
        cancel_handler(update)

list_callback_query_handler = CallbackQueryHandler(callback_query_handler)
list_raffle_handler = CommandHandler(['ver_sorteos', 'participar'], start)
