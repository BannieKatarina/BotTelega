import logging
import random
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from data import TOKEN

people = {'alexander2.jpg': ['александр ii', 'александр ii освободитель', 'александр 2', 'александр 2 освободитель'],
          'archimed.jpg': ['архимед'], 'dwaynejohnson.webp': ['дуэйн джонсон', 'скала', 'дуэйн скала джонсон'],
          'emelyanpugachov.jpg': ['емельян пугачёв'],
          'gagarin.jpg': ['гагарин', 'юрий гагарин', 'юрий алексеевич гагарин'],
          'garikharlamov.webp': ['гарик харламов', 'харламов'], 'jekichan.jfif': ['джеки чан'],
          'putin.jpg': ['путин', 'владимир путин', 'владимир владимирович путин'],
          'rogertdaunimladshiy.webp': ['роберт дауни младший'],
          'tomholland.webp': ['том холланд', 'холланд']}
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


def play_guess_person(update, context):
    update.message.reply_text('Угадайте человека')
    k = list(people.keys())
    r = random.randint(0, len(k) - 1)
    photo = 'guess_person/' + k[r]
    context.user_data['person'] = people[k[r]]
    update.message.reply_document(open(photo, 'rb'))
    return 1


def check_answer(update, context):
    if update.message.text.lower() in context.user_data['person']:
        update.message.reply_text('Вы угадали. Поздравляем!')
        return ConversationHandler.END
    else:
        update.message.reply_text('Вы не угадали. Поробуйте ещё.')
        return 1


def stop(update, context):
    update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('play_guess_person', play_guess_person)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={1: [MessageHandler(Filters.text & ~Filters.command, check_answer)]},
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)]
    )

    dp.add_handler(conv_handler)

    # text_handler = MessageHandler(Filters.text, ...)

    # dp.add_handler(text_handler)
    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
