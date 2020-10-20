import logging
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from bson import Binary

from src.db.models import Raffle

NAME, DESCRIPTION, PHOTO, MAX_NUMBERS = range(4)

def start(update, context):
    admin_name = update.message.from_user.name
    update.message.reply_text(
        f'Hola admin {admin_name}! Crea un nuevo sorteo siguiendo los pasos que te voy a ir describiendo.\n'
        'Primero, el nombre del sorteo...'
    )
    return NAME

def set_name(update, context):
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_text(
        f'El nombre {name} es realmente bonito. Ahora escribe una pequeña descripción. *Recuerda*, no '
        'puede exceder de 250 caracteres.'
    )
    return DESCRIPTION

def set_description(update, context):
    description = update.message.text
    context.user_data['description'] = description
    update.message.reply_text(
        f'Una foto sería bonita, no crees? Agrega una a continuación.'
    )
    return PHOTO

def set_photo(update, context):
    photo = update.message.photo[-1].get_file().download_as_bytearray()
    context.user_data['photo'] = Binary(photo)
    update.message.reply_text(
        f'Cuántos usuarios pueden optar por entrar en este sorteo?'
    )
    return MAX_NUMBERS

def set_max_numbers(update, context):
    max_numbers = update.message.text
    context.user_data['max_numbers'] = int(max_numbers)
    context.user_data['is_open'] = True

    logging.info(f'raffle_data - {context.user_data}')

    Raffle.objects.insert_one(context.user_data)

    context.user_data.clear()

    update.message.reply_text(
        f'Perfecto! Todo listo para el primer sorteo!'
    )
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
