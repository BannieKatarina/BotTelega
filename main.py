import logging
import random
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from data import TOKEN

people = {'alexander2.webp': ['александр ii', 'александр ii освободитель', 'александр 2', 'александр 2 освободитель'],
          'archimed.webp': ['архимед'], 'dwaynejohnson.webp': ['дуэйн джонсон', 'скала', 'дуэйн скала джонсон'],
          'emelyanpugachov.webp': ['емельян пугачёв'],
          'gagarin.webp': ['гагарин', 'юрий гагарин', 'юрий алексеевич гагарин'],
          'garikharlamov.webp': ['гарик харламов', 'харламов'], 'jekichan.webp': ['джеки чан'],
          'putin.webp': ['путин', 'владимир путин', 'владимир владимирович путин'],
          'robertdaunimladshiy.webp': ['роберт дауни младший'],
          'tomholland.webp': ['том холланд', 'холланд']}
characters = {'harrypotter.webp': ['гарри поттер', 'гарри джеймс поттер'],
              'ironman.webp': ['железный человек', 'тони старк'], 'leonardo.webp': ['леонардо', 'лео'],
              'sonic.webp': ['соник']}
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


def check_answer_play_guess_character(update, context):
    if update.message.text.lower() in context.user_data['character']:
        update.message.reply_text('Вы угадали. Поздравляем!')
        return ConversationHandler.END
    else:
        update.message.reply_text('Вы не угадали. Поробуйте ещё.')
        return 1


def check_answer_play_guess_person(update, context):
    if update.message.text.lower() in context.user_data['person']:
        update.message.reply_text('Вы угадали. Поздравляем!')
        return ConversationHandler.END
    else:
        update.message.reply_text('Вы не угадали. Поробуйте ещё.')
        return 1


def stop_guess_person(update, context):
    update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def play_guess_character(update, context):
    update.message.reply_text('Угадайте героя кино или мультика')
    k = list(characters.keys())
    r = random.randint(0, len(k) - 1)
    photo = 'guess_character/' + k[r]
    context.user_data['character'] = characters[k[r]]
    update.message.reply_document(open(photo, 'rb'))
    return 1


def stop_guess_character(update, context):
    update.message.reply_text("Всего доброго!")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    conv_handler_play_guess_person = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('play_guess_person', play_guess_person)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={1: [MessageHandler(Filters.text & ~Filters.command, check_answer_play_guess_person)]},
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop_guess_person', stop_guess_person)]
    )
    conv_handler_play_guess_character = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('play_guess_character', play_guess_character)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={1: [MessageHandler(Filters.text & ~Filters.command, check_answer_play_guess_character)]},
        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop_guess_character', stop_guess_character)]
    )

    dp.add_handler(conv_handler_play_guess_character)

    # text_handler = MessageHandler(Filters.text, ...)

    # dp.add_handler(text_handler)
    dp.add_handler(conv_handler_play_guess_person)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
