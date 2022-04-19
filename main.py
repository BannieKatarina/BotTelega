import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from data.data import tok
import random
import csv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = tok



def citys_start(update, context):
    with open('data/bots_citys.txt', 'rt', encoding='utf-8') as f:
        bots = [el.split('\n') for el in f.read().split('+')]
        context.user_data['bots_cityes'] = bots
        context.user_data['last_letter'] = 'А'
    reply_keyboard = [['Я сдаюсь', '/close', '/help_citys']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Вы начинаете первым", reply_markup=markup)
    return 1


def play_citys(update, context):
    bots = context.user_data['bots_cityes']
    letter = context.user_data['last_letter']
    with open('data/geo.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        sp = [el['city'] for el in reader]
    if update.message.text not in sp and update.message.text != 'Я сдаюсь':
        reply_keyboard = [['Я сдаюсь', '/close', '/help_citys']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Это не город! Попробуйте ещё раз.", reply_markup=markup)
        return 1
    if update.message.text[0] != letter and update.message.text != 'Я сдаюсь':
        reply_keyboard = [['Я сдаюсь', '/close', '/help_citys']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(f"Это не та буква! Вам нужно назвать город на букву \'{letter}\'",
                                  reply_markup=markup)
        return 1
    index = ord(update.message.text[-1].upper()) - ord('А') if update.message.text[-1] != 'ь' and update.message.text[
        -1] != 'ъ' else ord(update.message.text[-2].upper()) - ord('А')
    if update.message.text == 'Я сдаюсь':
        context.user_data['result'] = True
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Результаты готовы. Желаете посмотреть?", reply_markup=markup)
        return 2
    elif len(bots[index]) == 0:
        context.user_data['result'] = False
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Результаты готовы. Желаете посмотреть?", reply_markup=markup)
        return 2
    else:
        reply_keyboard = [['Я сдаюсь', '/close', '/help_citys']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        c = random.choice(bots[index])
        update.message.reply_text(c, reply_markup=markup)
        letter_new = c[-1] if c[-1] != 'ь' and c[-1] != 'ъ' else c[-2]
        bots[index].pop(bots[index].index(c))
        context.user_data['bots_cityes'] = bots
        context.user_data['last_letter'] = letter_new.upper()
        return 1


def result_citys(update, context):
    want_to_see = True if update.message.text == 'Да' else False
    if want_to_see:
        if context.user_data['result']:
            reply_keyboard = [['/start_citys', '/close']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text("Ура! Я победил!", reply_markup=markup)
            return ConversationHandler.END
        else:
            reply_keyboard = [['/start_citys', '/close']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text("Поздравляю! Вы выиграли!", reply_markup=markup)
            return ConversationHandler.END
    else:
        update.message.reply_text("Не хотите? Как хотите.")
        return ConversationHandler.END


def help_citys(update, context):
    reply_keyboard = [['Я сдаюсь', '/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("""Всё очень просто. Первый игрок называет город на букву \'А\', 
    а дальше игроки называют города на последнюю (или предпоследнюю букву, если город заканчивается на \'ь\' или \'ъ\').
    Игра продолжается до тех пор, пока бот не предложит показать результаты. Чтобы сдаться, игрок должен ввести фразу \'Я сдаюсь\'
    """, reply_markup=markup)
    return 1


def close_keyboard(update, context):
    update.message.reply_text(reply_markup=ReplyKeyboardRemove())


def stop(update, context):
    update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start_citys', citys_start)],

        states={
            1: [MessageHandler(Filters.text & ~Filters.command, play_citys)],
            2: [MessageHandler(Filters.text & ~Filters.command, result_citys)]
        }, fallbacks=[CommandHandler('stop', stop)])

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('close', close_keyboard))
    dp.add_handler(CommandHandler('help_citys', help_citys))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
