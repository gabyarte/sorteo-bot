import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler

from src.db.models import Raffle, User, Number
from src.utils.utils import show_raffle_preview, in_batches, notify_admins, list_raffles
from src.utils.emojis import PENSIVE, WINK, DANGER
from src.utils.markups import CANCEL_MARKUP


# TODO List raffle pagination
def start(update, context):
    user_id = update.message.from_user.id

    logging.info(f'[START] user_id - {user_id}')

    user = User.documents.get(user_id, 'telegram_id')
    if not user.is_blocked:
        raffles = Raffle.documents.find({'is_open': True})

        list_raffles(raffles, 'Lista de sorteos disponibles:', user_id, update, CANCEL_MARKUP)


def show_handler(raffle_id, user_id, query):
    options_markup = []
    user = User.documents.get(user_id, key='telegram_id')

    info = None
    another_raffle = user.can_participate_in_another_raffle()
    can_take_number = user.can_take_number(raffle_id)
    in_raffle = user.in_raffle(raffle_id)

    if (another_raffle and can_take_number) or (not another_raffle and can_take_number and in_raffle):
        options_markup.append(InlineKeyboardButton('Participar', callback_data=f'get/{raffle_id},{user_id}'))
    else:
        info = 'No puede escoger número de este sorteo'

    if in_raffle:
        options_markup.append(InlineKeyboardButton('Salir', callback_data=f'out/{raffle_id},{user_id}'))

    if user.is_admin:
        options_markup.append(InlineKeyboardButton('Participantes', callback_data=f'admin/{raffle_id}'))

    raffle = Raffle.documents.get(raffle_id)
    if raffle:
        show_raffle_preview(raffle, query, info=info, markup=InlineKeyboardMarkup([options_markup, CANCEL_MARKUP]))


def get_handler(raffle_id, user_id, query):
    raffle = Raffle.documents.get(raffle_id)
    logging.info(f'[HANDLER get] {raffle}')

    available_numbers = raffle.available_numbers()
    numbers_markup = []
    for numbers in in_batches(available_numbers, 4):
        markup = [InlineKeyboardButton(str(i), callback_data=f'choice/{raffle_id},{user_id},{i}') for i in numbers if i]
        numbers_markup.append(markup)

    query.edit_message_caption('Escoge un número disponible:')
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(numbers_markup + [CANCEL_MARKUP]))


def choice_handler(raffle_id, user_id, number, query):
    number = Number.documents.insert({'user_id': user_id, 'raffle_id': raffle_id, 'number': number})

    raffle = Raffle.documents.get(raffle_id)
    logging.info(f'[HANDLER choice] raffle - {raffle}')

    chat = query.bot.get_chat(user_id)
    notify_admins(f'El usuario [@{chat.username}]({chat.link}) '
                  f'escogió el número *{number.number}* en el sorteo _{raffle.name}_', chat)

    if raffle and len(raffle.taken_numbers()) == raffle.max_numbers:
        Raffle.documents.update({'_id': raffle._id}, {'$set': {'is_open': False}})
        notify_admins(f'Se agotaron los números en el sorteo {raffle.name}', chat)


    query.edit_message_caption(f'Felicidades! El número {number.number} dicen que es de la suerte {WINK}...')


def out_handler(raffle_id, user_id, query):
    Number.documents.delete({'user_id': user_id, 'raffle_id': raffle_id})

    raffle = Raffle.documents.get(raffle_id)
    if raffle and not raffle.is_open:
        Raffle.documents.update({'_id': raffle._id}, {'$set': {'is_open': True}})

    query.edit_message_caption(f'Sentimos verte partir {PENSIVE}')
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([CANCEL_MARKUP]))

    chat = query.bot.get_chat(user_id)
    notify_admins(f'El usuario [@{chat.username}]({chat.link}) ha salido del sorteo {raffle.name}', chat)


def cancel_handler(query):
    query.message.delete()


def admin_handler(raffle_id, query):
    participants = Number.documents.find({'raffle_id': raffle_id})

    grouped_participants = {}
    for participant in participants:
        if participant.user_id not in grouped_participants:
            grouped_participants[participant.user_id] = [participant.number]
        else:
            grouped_participants[participant.user_id] += [participant.number]

    logging.info(f'[HANDLER admin] grouped_participants - {grouped_participants}')

    list_participants = []
    for user_id, numbers in grouped_participants.items():
        chat = query.bot.get_chat(user_id)
        name = f'{chat.first_name} {chat.last_name}' if chat.first_name and chat.last_name else chat.username
        name = name if name else chat.first_name
        numbers_str = str(numbers)
        numbers_str = numbers_str[1:-1]
        logging.info(f'[HANDLER admin] name - {name}\n numbers_str - {numbers_str}')

        list_participants.append([InlineKeyboardButton(f'{name} ({numbers_str})', callback_data=f'block/{user_id}')])

    query.edit_message_caption(f'Participantes\n\n{DANGER} Si selecciones un participante, lo puedes *BLOQUEAR* y no podrá participar en ningún sorteo', parse_mode=ParseMode.MARKDOWN_V2)
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(list_participants + [CANCEL_MARKUP]))


def block_handler(user_id, query):
    User.documents.update({'telegram_id': user_id}, {'$set': {'is_blocked': True}})

    Number.documents.delete({'user_id': user_id})

    chat = query.bot.get_chat(user_id)

    query.message.reply_text(f'El usuario [@{chat.username}]({chat.link}) ha sido bloquedo', parse_mode=ParseMode.MARKDOWN_V2)


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

    if cmd == 'admin':
        raffle_id = options[0]
        logging.info(f'[HANDLER] raffle_id - {raffle_id}')
        admin_handler(raffle_id, query)

    if cmd == 'block':
        user_id = options[0]
        logging.info(f'[HANDLER] user_id - {user_id}')
        block_handler(user_id, query)

    if cmd == 'cancel':
        cancel_handler(query)

participate_callback_query_handler = CallbackQueryHandler(callback_query_handler)
participate_raffle_handler = CommandHandler(['ver_sorteos', 'participar'], start)
