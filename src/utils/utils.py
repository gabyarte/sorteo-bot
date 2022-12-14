from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup


def show_raffle_preview(raffle, updater, info='', markup=None):
    raffle_name = f'*{raffle.name.upper()}*'
    raffle_desc = raffle.description
    raffle_available = f'Disponibles {raffle.max_numbers - raffle.taken_numbers_count()}/{raffle.max_numbers}'

    raffle_description = f'{raffle_name}\n\n{raffle_desc}\n\n{raffle_available}'

    if info:
        raffle_description += f'\n\n_{info}_'

    updater.message.reply_photo(photo=raffle.photo,
                                caption=raffle_description,
                                parse_mode=ParseMode.MARKDOWN_V2,
                                reply_markup=markup)


def in_batches(iterator, size):
    batch = []
    for elem in iterator:
        batch.append(elem)
        if len(batch) == size:
            yield tuple(batch)
            batch = []

    if batch:
        fill = [None] * (size - len(batch))
        yield tuple(batch + fill)


def get_numbers(query):
    from src.db.models import Number

    return [number.number for number in Number.documents.find(query)]


def notify_admins(message, query):
    from src.db.models import User

    admins = User.documents.find({'is_admin': True})
    for admin in admins:
        query.bot.get_chat(admin.telegram_id).send_message(text=message, parse_mode=ParseMode.MARKDOWN_V2)


def list_raffles(raffles, message, user_id, updater, cancel=None):
    raffles_menu = []
    for raffle in raffles:
        raffles_menu.append([InlineKeyboardButton(f'{raffle.name} ({raffle.taken_numbers_count()}/{raffle.max_numbers})',
                                              callback_data=f'show/{raffle._id},{user_id}')])

    raffles_menu.append(cancel)
    updater.message.reply_text(message, reply_markup=InlineKeyboardMarkup(raffles_menu))
