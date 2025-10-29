import re
from logging import fatal

from festutimetable import FestuApi

from prefs import *
from get_chat_members import get_chat_members

import requests
import asyncio
import logger
import pytz
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tabulate import tabulate
import pickle
import festutimetable


from telebot.async_telebot import AsyncTeleBot
from telebot import types

from logger import baseLogger


##  telegram bot set_my_commands
# Чтение файла с настройками группы (id;группа)
with open('data.pickle', 'rb') as f:
    groupPrefs = pickle.load(f)

print(groupPrefs)

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
        # TODO Проверка есть ли юз
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

        if message.text == "/prefs@OniiChanMentionBot":
            await bot.send_message(message.chat.id, "Ответь на это сообщение названием группы, например: БО911ПИА", message_thread_id=msg_thread_id)
        if message.reply_to_message is not None:
            if message.reply_to_message.from_user.id == bot_id and (message.reply_to_message.text == "Ответь на это сообщение названием группы, например: БО911ПИА"):
                groupPrefs[message.chat.id] = message.text.upper().replace(' ', '')
                with open('data.pickle', 'wb') as f:
                    pickle.dump(groupPrefs, f)
                if message.text in groupId:
                    await bot.send_message(message.chat.id, "Теперь отправляется расписание группы" + " " + message.text, message_thread_id=msg_thread_id)
                else:
                    await bot.send_message(message.chat.id, "К сожалению расписание данной группы пока не настроено(или вы ошиблись в написании группы). Но группа присвоена и возможно будет добавлена в расписание", message_thread_id=msg_thread_id)


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


    if call.message.chat.id in groupPrefs:
        group_name = groupPrefs[call.message.chat.id]
    else:
        await bot.send_message(call.message.id, "Группа не настроена, настройте её с помощью /prefs@OniiChanMentionBot", message_thread_id=msg_thread_id)
        return

    if "today" in call.data:
        i = get_timetable_by_day(group_name, current_date)
        if len(i) < 10:
            await bot.send_message(call.message.chat.id,
                                   tag + "\n\n" + current_date + ": " + "Кажись пар нету",
                                   message_thread_id=msg_thread_id)
        await bot.send_message(call.message.chat.id,
                    i, message_thread_id=msg_thread_id)

    elif "tomorrow" in call.data:
        i = get_timetable_by_day(group_name, tomorrow_date)
        if len(i) < 10:
            await bot.send_message(call.message.chat.id,
                                   tag + "\n\n" + current_date + ": " + "Кажись пар нету",
                                   message_thread_id=msg_thread_id)
        await bot.send_message(call.message.chat.id,
                               i, message_thread_id=msg_thread_id)

def get_timetable_by_day(group: str, date: str):
    festu_service = FestuApi.TimetableService()
    k = festu_service.get_timetable_by_day(group, date)
    ret = ["⚡️⚡️⚡️⚡️⚡️⚡️ \n", k.date]


    for i in range(len(k.lectures)):
        if k.lectures[i].teacher == "":
            ret.append("\n" + k.lectures[i].time + "\n" + re.sub(r'[^а-яА-Я0-9ёЁ ()]', '', k.lectures[i].name) +
                       k.lectures[i].teacher + "\n" + k.lectures[i].classroom)
        else:
            ret.append("\n" + k.lectures[i].time + "\n" + re.sub(r'[^а-яА-Я0-9ёЁ ()]', '', k.lectures[i].name) + "\n" +
                k.lectures[i].teacher + "\n" + k.lectures[i].classroom)
    return "\n".join(ret)

asyncio.run(bot.polling())