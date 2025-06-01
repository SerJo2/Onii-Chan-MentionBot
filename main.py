from pyexpat.errors import messages

from prefs import *
from get_chat_members import get_chat_members

import asyncio
import logger

from telebot.async_telebot import AsyncTeleBot

from logger import baseLogger


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


        if message.text == "/all":
            chat_members = await get_chat_members(message.chat.id)
            baseLogger.info("chat_members: " + str(chat_members))
            for i in range(1, len(chat_members), 5):
                group = chat_members[i:i+5]
                send = ""
                for j in group:
                    k = "@" + j
                    send = send + k + " "
                await bot.send_message(message.chat.id, send, message_thread_id=msg_thread_id)
        if message.text == "/ping":
            await bot.send_message(message.chat.id, "Бот работает", message_thread_id=msg_thread_id)
        if message.text == "/ocHelp":
            await bot.send_message(message.chat.id, "/all - Пинг всех в группе \n/ping - Проверка онлайна бота", message_thread_id=msg_thread_id)

        if message.chat.id == my_chat_id:
            if message.text == "":
                pass
    except BaseException as be:
        await bot.send_message(message.chat.id, "напишите @psibladeabuzerz \n" + "Что-то пошло не так. Лог ниже \n" % be)
        baseLogger.critical("Ошибка в get_text_messages", exc_info=True)


asyncio.run(bot.polling())