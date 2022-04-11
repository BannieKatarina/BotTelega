import logging
from telegram.ext import Updater, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# здесь - клавиатуры

TOKEN = 'BOT_TOKEN'


# здесь будут команды для бота

def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    # text_handler = MessageHandler(Filters.text, ...)

    # dp.add_handler(text_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
