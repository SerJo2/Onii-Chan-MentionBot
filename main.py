
from prefs import token
from get_chat_members import get_chat_members

import asyncio

from telebot.async_telebot import AsyncTeleBot
print("ok")
API_TOKEN = token


bot = AsyncTeleBot(API_TOKEN)
print("bot set up")
@bot.message_handler(content_types=['text'])
async def get_text_messages(message):
    print(message.text)
    if message.text == "/all":
        print("before func")
        chat_members = await get_chat_members(message.chat.id)
        print(chat_members)
        for i in range(1, len(chat_members), 5):
            group = chat_members[i:i+5]
            send = ""
            for j in group:
                k = "@" + j
                send = send + k + " "
            await bot.send_message(message.chat.id, send)


asyncio.run(bot.polling())