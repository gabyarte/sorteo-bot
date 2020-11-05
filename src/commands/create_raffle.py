import logging
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

from src.db.models import Raffle
from src.utils.utils import show_raffle_preview

NAME, DESCRIPTION, PHOTO, MAX_NUMBERS = range(4)


def start(update, context):
    admin_name = update.message.from_user.name
    update.message.reply_text(
        f'Hola admin {admin_name}! Crea un nuevo sorteo siguiendo los pasos que te voy a ir describiendo.\n\n'
        'Primero, el nombre del sorteo...'
    )
    return NAME


def set_name(update, context):
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_text(
        f'El nombre *{name}* es realmente bonito\. Ahora escribe una pequeña descripción\.',
        parse_mode=ParseMode.MARKDOWN_V2)
    return DESCRIPTION


def set_description(update, context):
    description = update.message.text
    context.user_data['description'] = description
    update.message.reply_text(f'Una foto sería bonita, no crees? Agrega una a continuación.')
    return PHOTO


def set_photo(update, context):
    photo = update.message.photo[-1].get_file().file_id
    context.user_data['photo'] = photo
    update.message.reply_text(f'Cuántos usuarios pueden optar por entrar en este sorteo?')
    return MAX_NUMBERS


def set_max_numbers(update, context):
    max_numbers = update.message.text

    raffle_data = context.user_data
    raffle_data['max_numbers'] = int(max_numbers)
    raffle_data['is_open'] = True

    logging.info(f'raffle_data - {raffle_data}')

    raffle = Raffle.documents.insert(raffle_data)
    logging.info(f'raffle - {raffle}')
    if raffle:
        show_raffle_preview(raffle, update)

    context.user_data.clear()

    update.message.reply_text(f'Perfecto! Todo listo para el sorteo!')
    return ConversationHandler.END


create_raffle_handler = ConversationHandler(
    entry_points=[CommandHandler('crear_sorteo', start)],
    states={
        NAME: [MessageHandler(Filters.text, set_name)],
        DESCRIPTION: [MessageHandler(Filters.text, set_description)],
        PHOTO: [MessageHandler(Filters.photo, set_photo)],
        MAX_NUMBERS: [MessageHandler(Filters.regex('^\d+$'), set_max_numbers)]
    },
    fallbacks=[]
)
