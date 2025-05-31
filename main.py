
from prefs import *
from get_chat_members import get_chat_members

import asyncio
import logging

from telebot.async_telebot import AsyncTeleBot

logging.info("Main.py started")
API_TOKEN = token

bot = AsyncTeleBot(API_TOKEN)
logging.info("Bot was set up")
@bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    try:
        logging.info("message.text: " + message.text)
        logging.info("message.chat.id: " + message.chat.id)


        if message.text == "/all":
            chat_members = await get_chat_members(message.chat.id)
            logging.info("chat_members: " + chat_members)
            for i in range(1, len(chat_members), 5):
                group = chat_members[i:i+5]
                send = ""
                for j in group:
                    k = "@" + j
                    send = send + k + " "
                await bot.send_message(message.chat.id, send)
        if message.text == "/ping":
            await bot.send_message(message.chat.id, "Бот работает")
        if message.text == "/help":
            await bot.send_message(message.chat.id, "/all - Пинг всех в группе \n /ping - Проверка онлайна бота")

        if message.chat.id == my_chat_id:
            if message.text == "":
                pass
    except BaseException as be:
        await bot.send_message(message.chat.id, "напишите @psibladeabuzerz \n" + "Что-то пошло не так. Лог ниже \n" % be)
        logging.critical("Ошибка в get_text_messages", exc_info=True)


asyncio.run(bot.polling())