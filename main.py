import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from data.data import tok
import sqlite3
import requests
import random
import csv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = tok


def start(update, context):
    update.message.reply_text("""Этот бот может поиграть с Вами в \'Города\', \'Угадай человека\' и некоторые другие.
Подробнее \'/help\'.""")


def help(update, context):
    update.message.reply_text("""/start_cityes - играть в \'Города\';
/start_labyrint - играть в \'Лабиринт\'
/start_countries - играть в \'Угадай страну по карте\'""")


def cityes_start(update, context):
    with open('data/bots_cityes.txt', 'rt', encoding='utf-8') as f:
        bots = [el.split('\n') for el in f.read().split('+')]
        context.user_data['bots_cityes'] = bots
        context.user_data['last_letter'] = 'А'
    reply_keyboard = [['Я сдаюсь', '/close', '/help_cityes']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Вы начинаете первым", reply_markup=markup)
    return 1


def play_cityes(update, context):
    bots = context.user_data['bots_cityes']
    letter = context.user_data['last_letter']
    with open('data/geo.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        sp = [el['city'] for el in reader]
    if update.message.text not in sp and update.message.text != 'Я сдаюсь':
        reply_keyboard = [['Я сдаюсь', '/close', '/help_cityes']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("Это не город! Попробуйте ещё раз.", reply_markup=markup)
        return 1
    if update.message.text[0] != letter and update.message.text != 'Я сдаюсь':
        reply_keyboard = [['Я сдаюсь', '/close', '/help_cityes']]
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
        reply_keyboard = [['Я сдаюсь', '/close', '/help_cityes']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        c = random.choice(bots[index])
        update.message.reply_text(c, reply_markup=markup)
        letter_new = c[-1] if c[-1] != 'ь' and c[-1] != 'ъ' else c[-2]
        bots[index].pop(bots[index].index(c))
        context.user_data['bots_cityes'] = bots
        context.user_data['last_letter'] = letter_new.upper()
        return 1


def result_cityes(update, context):
    want_to_see = True if update.message.text == 'Да' else False
    if want_to_see:
        if context.user_data['result']:
            reply_keyboard = [['/start_cityes', '/close']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text("Ура! Я победил!", reply_markup=markup)
            return ConversationHandler.END
        else:
            reply_keyboard = [['/start_cityes', '/close']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text("Поздравляю! Вы выиграли!", reply_markup=markup)
            return ConversationHandler.END
    else:
        update.message.reply_text("Не хотите? Как хотите.")
        return ConversationHandler.END


def help_cityes(update, context):
    reply_keyboard = [['Я сдаюсь', '/close']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = "Всё очень просто. Первый игрок называет город на букву \'А\', "
    text += "а дальше игроки называют города на последнюю (или предпоследнюю букву, если город заканчивается на \'ь\'"
    text += " или \'ъ\'). Игра продолжается до тех пор, пока бот не предложит показать результаты."
    text += " Чтобы сдаться, игрок должен ввести фразу \'Я сдаюсь\'"
    update.message.reply_text(text, reply_markup=markup)
    return 1


def start_labyrint(update, context):
    reply_keyboard = [['Направо', 'Налево'], ['Прямо', '/help_labyrint']]
    context.user_data["ways"] = reply_keyboard
    context.user_data["items"] = []
    context.user_data["act"] = 1
    context.user_data["blok"] = False
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = "Добро пожаловать в лабиринт. Вам нужно выбраться отсюда. В лабиринте два выхода."
    text += "Вы можете пойти \"направо\", \"налево\" или \"прямо\"."
    update.message.reply_text(text, reply_markup=markup)
    return 1


def help_labyrint(update, context):
    reply_keyboard = context.user_data["ways"]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text = "Это лабиринт. Вы выбираете куда пойти, выбирая варианты клавиатуры, в попытках найти выход."
    text += "Здесь несколько концовок."
    update.message.reply_text(text, reply_markup=markup)
    return context.user_data["act"]


def first_act(update, context):
    if update.message.text == "Прямо":
        if "Ключ" in context.user_data["items"]:
            reply_keyboard = [['/start_labyrint', '/close']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text("Вы использовали ключ.")
            text = "Вы пошли прямо. Здесь темно. Вы упали в какую-то жидкость. Эта яма наполнена кислотой"
            text += ", и она слишком глубокая, чтобы выбраться. Не повезло."
            update.message.reply_text(text)
            update.message.reply_text("Плохая концовка (1/6)", reply_markup=markup)
            return ConversationHandler.END
        else:
            reply_keyboard = [['Направо', 'Налево'], ['Прямо', '/help_labyrint']]
            context.user_data["ways"] = reply_keyboard
            context.user_data["act"] = 1
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            text = "Здесь железная дверь. Не пройти."
            text += "Вы можете пойти \"направо\", \"налево\" или \"прямо\"."
            update.message.reply_text(text, reply_markup=markup)
            return 1
    elif update.message.text == "Направо":
        reply_keyboard = [['Направо', 'Налево'], ['Назад', '/help_labyrint']]
        context.user_data["ways"] = reply_keyboard
        context.user_data["act"] = 2.1
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы пошли направо. Здесь развилка. Куда пойдем, \"налево\" или \"направо\"?"
        update.message.reply_text(text, reply_markup=markup)
        return 2.1
    else:
        if not context.user_data["blok"]:
            reply_keyboard = [['Направо', 'Прямо', 'Налево'], ['Назад', '/help_labyrint']]
        else:
            reply_keyboard = [['Прямо', 'Налево'], ['Назад', '/help_labyrint']]
        context.user_data["ways"] = reply_keyboard
        context.user_data["act"] = 2.2
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        s = ' \"направо\", ' if not context.user_data['blok'] else ' '
        text = f"Здесь развилка:{s}"
        text += "\"прямо\" или \"налево\"?"
        update.message.reply_text(text, reply_markup=markup)
        return 2.2


def second_act_one(update, context):
    if update.message.text == "Назад":
        reply_keyboard = [['Направо', 'Налево'], ['Прямо', '/help_labyrint']]
        context.user_data["ways"] = reply_keyboard
        context.user_data["act"] = 1
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы можете пойти \"направо\", \"налево\" или \"прямо\"."
        update.message.reply_text(text, reply_markup=markup)
        return 1
    elif update.message.text == "Направо":
        reply_keyboard = [['/start_labyrint', '/close']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы пошли направо. Это место похоже на берлогу. Это не к добру. "
        text += "Судя по шагам, которые эхом доносятся до Вас, зверь вернулся! Это медведь! "
        text += "Я не думаю, что он предложит чашку чая."
        update.message.reply_text(text)
        update.message.reply_text("Плохая концовка (2/6)", reply_markup=markup)
        return ConversationHandler.END
    elif update.message.text == "Налево":
        reply_keyboard = [['/start_labyrint', '/close']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы пошли налево. Вы идёте по длинному коридору. Но что это? В конце виден дневной свет!"
        text += " Да здравствует свобода!!!"
        update.message.reply_text(text)
        update.message.reply_text("Хорошая концовка (3/6)", reply_markup=markup)
        return ConversationHandler.END


def second_act_two(update, context):
    if update.message.text == "Назад":
        reply_keyboard = [['Направо', 'Налево'], ['Прямо', '/help_labyrint']]
        context.user_data["ways"] = reply_keyboard
        context.user_data["act"] = 1
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы можете пойти \"направо\", \"налево\" или \"прямо\"."
        update.message.reply_text(text, reply_markup=markup)
        return 1
    elif update.message.text == "Направо":
        reply_keyboard = [['Ключ', 'Рисовый пирожок'], ['/help_labyrint']]
        context.user_data["ways"] = reply_keyboard
        context.user_data["act"] = 3.1
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы находите какой-то ключ и ... рисовый пирожок. Что возьмём?"
        update.message.reply_text(text, reply_markup=markup)
        return 3.1
    elif update.message.text == "Налево":
        text = "Вы пошли налево. Вы видите ... домик?! Что ж, он выглядит мило. Здесь живёт кто-то?"
        text += " Вы постучали в дверь. Её открыл кролик.\n"
        text += "\'Если дашь мне что-нибудь интересное, то ты можешь остаться у меня.\' - сказал кролик."
        update.message.reply_text(text)
        if "Рисовый пирожок" in context.user_data["items"]:
            reply_keyboard = [['/start_labyrint', '/close']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            text = "\nВы отдаёте рисовый пирожок. Кролик приглашает Вас жить с ним."
            update.message.reply_text(text)
            update.message.reply_text("Нейтральная концовка (4/6)", reply_markup=markup)
            return ConversationHandler.END
        elif "Ключ" in context.user_data["items"]:
            if not context.user_data["blok"]:
                reply_keyboard = [['Направо', 'Прямо', 'Налево'], ['Назад', '/help_labyrint']]
            else:
                reply_keyboard = [['Прямо', 'Налево'], ['Назад', '/help_labyrint']]
            context.user_data["ways"] = reply_keyboard
            context.user_data["act"] = 2.2
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            text = "\nВы предлагаете ключ. Кролик не пускает Вас. Вы возвращаетесь назад.\n"
            s = ' \"направо\", ' if not context.user_data['blok'] else ' '
            text += f"Здесь развилка:{s}"
            text += "\"прямо\" или \"налево\"?"
            update.message.reply_text(text, reply_markup=markup)
            return 2.2
        else:
            if not context.user_data["blok"]:
                reply_keyboard = [['Направо', 'Прямо', 'Налево'], ['Назад', '/help_labyrint']]
            else:
                reply_keyboard = [['Прямо', 'Налево'], ['Назад', '/help_labyrint']]
            context.user_data["ways"] = reply_keyboard
            context.user_data["act"] = 2.2
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            text = "\nВы возвращаетесь назад, ведь вам нечего предложить.\n"
            s = ' \"направо\", ' if not context.user_data['blok'] else ' '
            text += f"Здесь развилка:{s}"
            text += "\"прямо\" или \"налево\"?"
            update.message.reply_text(text, reply_markup=markup)
            return 2.2
    else:
        reply_keyboard = [['Направо', 'Налево'], ['Назад', '/help_labyrint']]
        context.user_data["ways"] = reply_keyboard
        context.user_data["act"] = 3.2
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы пошли прямо. Очередная развилка: \"направо\" или \"налево\"?"
        update.message.reply_text(text, reply_markup=markup)
        return 3.2


def third_act_one(update, context):
    context.user_data["blok"] = True
    if update.message.text == "Ключ":
        context.user_data["items"] += ["Ключ"]
    else:
        context.user_data["items"] += ["Рисовый пирожок"]
    text = f"Вы взяли {context.user_data['items'][0]}. Стена начала двигаться."
    text += "Вы успеваете проскочить назад. Больше туда не пройти."
    reply_keyboard = [['Прямо', 'Налево'], ['Назад', '/help_labyrint']]
    context.user_data["ways"] = reply_keyboard
    context.user_data["act"] = 2.2
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    text += f"Здесь развилка: \"прямо\" или \"налево\"?"
    update.message.reply_text(text, reply_markup=markup)
    return 2.2


def third_act_two(update, context):
    if update.message.text == "Назад":
        if not context.user_data["blok"]:
            reply_keyboard = [['Направо', 'Прямо', 'Налево'], ['Назад', '/help_labyrint']]
        else:
            reply_keyboard = [['Прямо', 'Налево'], ['Назад', '/help_labyrint']]
        context.user_data["ways"] = reply_keyboard
        context.user_data["act"] = 2.2
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        s = ' \"направо\", ' if not context.user_data['blok'] else ' '
        text = f"Здесь развилка:{s}"
        text += "\"прямо\" или \"налево\"?"
        update.message.reply_text(text, reply_markup=markup)
        return 2.2
    elif update.message.text == "Направо":
        reply_keyboard = [['/start_labyrint', '/close']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Вы пошли направо. Вы пришли в бункер. Здесь есть еда, вода, постель и другие вещи."
        text += " Вы решили остаться здесь."
        update.message.reply_text(text)
        update.message.reply_text("Нейтральная концовка (5/6)", reply_markup=markup)
        return ConversationHandler.END
    else:
        reply_keyboard = [['/start_labyrint', '/close']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = "Это ... Дверь с надписью \"выход\"... Видите: В. Ы. Х. О. Д."
        text += " Простите, но мне больше нечего сказать -_-"
        update.message.reply_text(text)
        update.message.reply_text("Нейтральная концовка (5/6)", reply_markup=markup)
        return ConversationHandler.END


def help_countries(update, context):
    text = 'В этой игре надо угадать город по карте. Карта типа '
    text += '\"Гибрид\". На карте будет одна из знаменитых достопримечательностей. У Вас три попытки. '
    text += 'После трёх попыток будет показан правильный ответ и достопримечательность, изображенная '
    text += 'на карте. Когда игра закончиться, бот покажет вам сколько стран Вы смогли отгадать.'
    update.message.reply_text(text)


def select_country(sp):
    if sp:
        con = sqlite3.connect('data/bots_countries.db')
        cur = con.cursor()
        index = random.choice(sp)
        lon, lat = cur.execute(f"""SELECT longitudes, latitudes FROM Countries WHERE id={index}""").fetchone()
        api_server = "http://static-maps.yandex.ru/1.x/"
        params = {
            "ll": ",".join([str(lon), str(lat)]),
            "spn": '0.0002,0.0002',
            "l": "sat,skl"
        }
        response = requests.get(api_server, params=params)
        return index, response.url
    else:
        return 0, 'Страны закончились.'


def start_countries(update, context):
    if 'countries' not in context.user_data:
        reply_keyboard = [['/help_countries']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        context.user_data['countries'] = [i for i in range(1, 23)]
        context.user_data['country_tries'] = 3
        context.user_data['right_country_count'] = 0
        context.user_data['all_country_count'] = 0
        context.user_data['country_task'], image = select_country(context.user_data['countries'])
        update.message.reply_text(image)
        update.message.reply_text('Что это за страна?', reply_markup=markup)
        return 1
    else:
        if context.user_data['countries']:
            reply_keyboard = [['Да', 'Нет']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            context.user_data['countries_play'] = True
            text = 'Вы отгадали все страны, которые я мог вам предложить. '
            text += 'Хотите обновить игру?'
            update.message.reply_text(text, reply_markup=markup)
            return 2
        else:
            reply_keyboard = [['Да', 'Нет']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            context.user_data['countries_play'] = False
            text = 'Вы уже играли в это игру. Хотите продолжить или обновить игру?'
            update.message.reply_text(text, reply_markup=markup)
            return 2


def check_country(update, context):
    con = sqlite3.connect('data/bots_countries.db')
    cur = con.cursor()
    right_country, landmark = cur.execute(f"""SELECT country, landmark FROM Countries
        WHERE id={context.user_data['country_task']}""").fetchone()
    if update.message.text == right_country:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = 'Поздравляю! Это правильный ответ. '
        text += f'Это {landmark}. Продолжить?'
        context.user_data['right_country_count'] += 1
        context.user_data['all_country_count'] += 1
        context.user_data['countries'].remove(context.user_data['country_task'])
        update.message.reply_text(text, reply_markup=markup)
        return 3
    elif update.message.text != right_country and context.user_data['country_tries'] > 1:
        context.user_data['country_tries'] -= 1
        text = f'Вы не отгадали. У вас осталось {context.user_data["country_tries"]} '
        text += f'попытк{"и" if context.user_data["country_tries"] == 2 else "а"}.'
        update.message.reply_text(text)
        return 1
    else:
        text = f'Вы не отгадали. Это {right_country}. '
        text += f'Достопримечательность - {landmark}. Продолжить?'
        context.user_data['all_country_count'] += 1
        reply_keyboard = [['Да', 'Нет']]
        context.user_data['countries'].remove(context.user_data['country_task'])
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(text, reply_markup=markup)
        return 3


def reset_countries(update, context):
    if update.message.text == 'Да':
        context.user_data['countries'] = [i for i in range(1, 23)]
        context.user_data['country_tries'] = 3
        context.user_data['right_country_count'] = 0
        context.user_data['all_country_count'] = 0
        context.user_data['country_task'], image = select_country(context.user_data['countries'])
        update.message.reply_text(image)
        update.message.reply_text('Что это за страна?')
        return 1
    else:
        if not context.user_data['countries_play']:
            update.message.reply_text('Будем играть с тем, что есть.')
            context.user_data['country_tries'] = 3
            context.user_data['right_country_count'] = 0
            context.user_data['all_country_count'] = 0
            context.user_data['country_task'], image = select_country(context.user_data['countries'])
            update.message.reply_text(image)
            update.message.reply_text('Что это за страна?')
            return 1
        else:
            update.message.reply_text('Тогда до свидания.')
            return ConversationHandler.END


def country_sel(update, context):
    if update.message.text == 'Да':
        reply_keyboard = [['/help_countries']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        context.user_data['country_tries'] = 3
        context.user_data['country_task'], image = select_country(context.user_data['countries'])
        if context.user_data['country_task'] != 0:
            update.message.reply_text(image)
            update.message.reply_text('Что это за страна?', reply_markup=markup)
            return 1
        else:
            reply_keyboard = [['/start_countries', '/close']]
            markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(image, reply_markup=markup)
            text = f'Вы отгадали {context.user_data["right_country_count"]} из '
            text += f'{context.user_data["all_country_count"]}'
            update.message.reply_text(text, reply_markup=markup)
            return ConversationHandler.END
    else:
        reply_keyboard = [['/start_countries', '/close']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = f'Вы отгадали {context.user_data["right_country_count"]} из '
        text += f'{context.user_data["all_country_count"]}'
        update.message.reply_text(text, reply_markup=markup)
        return ConversationHandler.END


def close_keyboard(update, context):
    update.message.reply_text("Ок!", reply_markup=ReplyKeyboardRemove())


def stop(update, context):
    update.message.reply_text("Хорошо!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher

    city_handler = ConversationHandler(
        entry_points=[CommandHandler('start_cityes', cityes_start)],
        states={1: [MessageHandler(Filters.text & ~Filters.command, play_cityes)],
                2: [MessageHandler(Filters.text & ~Filters.command, result_cityes)]},
        fallbacks=[CommandHandler('stop', stop)])
    labyrint_handler = ConversationHandler(
        entry_points=[CommandHandler('start_labyrint', start_labyrint)],
        states={1: [MessageHandler(Filters.text & ~Filters.command, first_act)],
                2.1: [MessageHandler(Filters.text & ~Filters.command, second_act_one)],
                2.2: [MessageHandler(Filters.text & ~Filters.command, second_act_two)],
                3.1: [MessageHandler(Filters.text & ~Filters.command, third_act_one)],
                3.2: [MessageHandler(Filters.text & ~Filters.command, third_act_two)]},
        fallbacks=[CommandHandler('stop', stop)])
    countries_handler = ConversationHandler(
        entry_points=[CommandHandler('start_countries', start_countries)],
        states={1: [MessageHandler(Filters.text & ~Filters.command, check_country)],
                2: [MessageHandler(Filters.text & ~Filters.command, reset_countries)],
                3: [MessageHandler(Filters.text & ~Filters.command, country_sel)]},
        fallbacks=[CommandHandler('stop', stop)])
    dp.add_handler(city_handler)
    dp.add_handler(labyrint_handler)
    dp.add_handler(countries_handler)
    dp.add_handler(CommandHandler('close', close_keyboard))
    dp.add_handler(CommandHandler('help_cityes', help_cityes))
    dp.add_handler(CommandHandler('help_labyrint', help_labyrint))
    dp.add_handler(CommandHandler('help_countries', help_countries))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
