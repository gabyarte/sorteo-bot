from telegram import ParseMode

def show_raffle_preview(raffle, update):
    text = f'*{raffle.name.upper()}*\n\n_{raffle.description}_'
    update.message.reply_photo(photo=raffle.photo, caption=text, parse_mode=ParseMode.MARKDOWN_V2)