from telegram import ParseMode


def show_raffle_preview(raffle, updater, info='', markup=None):
    raffle_description = f'''
    *{raffle.name.upper()}*
    
    {raffle.description}
    
    Disponibles {raffle.taken_numbers_count()}/{raffle.max_numbers}'''

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