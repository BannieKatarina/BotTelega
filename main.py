import logging
from random import randint
from telegram.ext import Updater, MessageHandler, Filters
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


def play_guess_person(update, photo):
    update.message.reply_text('Угадай человека')
    k = list(people.keys())
    r = random.randint(0, len(k) - 1)
    photo = k[r]
    update.message.send_photo(photo)
    m = update.message.text
    while m.lower() not in people[photo]:
        update.message.reply_text('Неверно, подумайте ещё')
        m = update.message.text



def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    # text_handler = MessageHandler(Filters.text, ...)

    # dp.add_handler(text_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
