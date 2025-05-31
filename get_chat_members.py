from telethon import TelegramClient
from prefs import *
import logging

logging.info("Telethon was started")

client = TelegramClient('session_name', api_id, api_hash)
logging.info("Telethon client was set up")
async def get_chat_members(chat_id):
    logging.info("Telethon func start")
    await client.start(bot_token=token)
    chat_members = []
    async for member in client.iter_participants(chat_id):
        chat_members.append(member.username)
    await client.disconnect()
    logging.info("Telethon disconnected")
    return chat_members