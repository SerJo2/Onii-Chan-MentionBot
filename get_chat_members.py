from telethon import TelegramClient
from prefs import *
import logger

from logger import baseLogger

baseLogger.info("Telethon was started")

client = TelegramClient('session_name', api_id, api_hash)
baseLogger.info("Telethon client was set up")
async def get_chat_members(chat_id):
    baseLogger.info("Telethon func start")
    await client.start(bot_token=token)
    chat_members = []
    async for member in client.iter_participants(chat_id):
        chat_members.append(member.username)
    await client.disconnect()
    baseLogger.info("Telethon disconnected")
    return chat_members