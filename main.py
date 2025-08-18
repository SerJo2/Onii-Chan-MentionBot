from logging import fatal

from prefs import *
from get_chat_members import get_chat_members

import requests
import asyncio
import logger
import pytz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tabulate import tabulate


from telebot.async_telebot import AsyncTeleBot
from telebot import types

from logger import baseLogger


##  telegram bot set_my_commands

tz = pytz.timezone('Asia/Vladivostok')
khabarovskTime = datetime.now(tz)
current_date = khabarovskTime.strftime('%d.%m.%Y')
data['Time'] = current_date
print(current_date)
baseLogger.info("Main.py started")
API_TOKEN = token
bot = AsyncTeleBot(API_TOKEN)
baseLogger.info("Bot was set up")

@bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    try:
        baseLogger.info("message.text: " + str(message.text))
        baseLogger.info("message.chat.id: " + str(message.chat.id))

        try:
            msg_thread_id = message.reply_to_message.message_thread_id
        except AttributeError:
            msg_thread_id = "General"


        if message.text == "/all@OniiChanMentionBot":
            chat_members = await get_chat_members(message.chat.id)
            baseLogger.info("chat_members: " + str(chat_members))
            for i in range(0, len(chat_members), 5):
                group = chat_members[i:i+5]
                send = ""
                for j in group:
                    k = "@" + j
                    send = send + k + " "
                baseLogger.info(send)
                await bot.send_message(message.chat.id, send, message_thread_id=msg_thread_id)
        if message.text == "/ping@OniiChanMentionBot":
            await bot.send_message(message.chat.id, "Бот работает", message_thread_id=msg_thread_id)
        if message.text == "/ochelp@OniiChanMentionBot":
            await bot.send_message(message.chat.id, "/all@OniiChanMentionBot - Пинг всех в группе \n/ping@OniiChanMentionBot - Проверка онлайна бота \n/tt@OniiChanMentionBot - Расписание", message_thread_id=msg_thread_id)

        if message.text == "/tt@OniiChanMentionBot":

            markup = types.InlineKeyboardMarkup()
            today = types.InlineKeyboardButton("Сегодня", callback_data='today')
            tomorrow = types.InlineKeyboardButton("Завтра", callback_data='tomorrow')
            markup.add(today)
            markup.add(tomorrow)

            await bot.send_message(message.chat.id,
                             "Когда?".format(message.from_user),
                             reply_markup=markup, message_thread_id=msg_thread_id)

        if message.chat.id == my_chat_id:
            if message.text == "":
                pass
    except BaseException as e:
        await bot.send_message(message.chat.id, f"Ошибка: {str(e)}. Отпишите @psibladeabuzerz")
        baseLogger.exception(e)


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    global khabarovskTime
    global current_date

    khabarovskTime = datetime.now(tz)
    current_date = khabarovskTime.strftime('%d.%m.%Y')  # Текущая дата в Хабре
    tomorrow_date = khabarovskTime + timedelta(days=1)
    tomorrow_date = tomorrow_date.strftime('%d.%m.%Y')

    tag = "@" + str(call.from_user.username)
    try:
        msg_thread_id = call.message.reply_to_message.message_thread_id
    except AttributeError:
        msg_thread_id = "General"


    if "today" in call.data:
        data['Time'] = current_date
        tableList = get_timetable_list()
        yesLessons = False
        for i in tableList:
            if i[:10] == current_date:
                yesLessons = True
                await bot.send_message(call.message.chat.id,
                                i, message_thread_id=msg_thread_id)
        if not yesLessons:
            await bot.send_message(call.message.chat.id,
                                   tag + "\n\n" + current_date + ": " + "Кажись пар нету", message_thread_id=msg_thread_id)

    elif "tomorrow" in call.data:
        data['Time'] = tomorrow_date
        tableList = get_timetable_list()
        yesLessons = False
        for i in tableList:
            if i[:10] == tomorrow_date:
                yesLessons = True
                await bot.send_message(call.message.chat.id,
                                 i, message_thread_id=msg_thread_id)
        if not yesLessons:
            await bot.send_message(call.message.chat.id,
                                   tag + "\n\n" + tomorrow_date + ": " +"Кажись пар нету", message_thread_id=msg_thread_id)

def get_timetable_list():
    print("1")
    responseTimetable = requests.post('https://www.dvgups.ru/index.php', params=params, cookies=cookies, headers=headers, data=data)
    table = responseTimetable.text

    printed_list = []
    print("2")
    root = BeautifulSoup(table, 'html.parser')
    all_dates = root.find_all('h3')
    trs = root.find_all('table')
    for i in range(len(trs)):
        printed_table = ""
        for_root = BeautifulSoup(str(trs[i]), 'html.parser')
        for_trs = for_root.select_one('table').select('tr')
        rows = [
            [td.text for td in tr.select('td')]
            for tr in for_trs[0:]
        ]

        final_table = list()
        for x in range(len(rows)):
            final_table.append([])
        ## print(final_table)

        #rows[x][z] - z: 0 - номер пары, z: 1 - что за пара, z: 2 - аудитория, z: 3 - группы, z:4 - препод

        ## print(rows)
        for j in range(len(rows)):
            for z in range(len(rows[j])):
                if z != 3:
                    final_table[j].append(rows[j][z]) # Убираем бесполезный z: 3, и оставляем все остальное

        ## print(final_table)
        for_date = str(all_dates[i]) # даты

        ## print(for_date[4:-5])
        ## print(tabulate(final_table, headers=[], tablefmt="grid"))
        printed_table += for_date[4:-5].strip().rstrip().rstrip('\n') + "\n" # дата
        for j in range(len(final_table)):
            s = ''
            for z in range(len(final_table[j])):
                s += final_table[j][z].strip().rstrip().rstrip('\n') + "\n"
            printed_table += s + "\n"
        printed_table += "----------------------------------------------" + "\n" # конец расписания текущей даты
        printed_list.append(printed_table)
    return printed_list

asyncio.run(bot.polling())