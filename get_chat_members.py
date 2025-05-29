from telethon import TelegramClient
from prefs import *
print("telethon start")
client = TelegramClient('session_name', api_id, api_hash)
print("telethon setted up")
async def get_chat_members(chat_id):
    print("telethon func start")
    await client.start(bot_token=token)
    chat_members = []
    print("telerhon before for")
    async for member in client.iter_participants(chat_id):
        print("telethon iteration")
        chat_members.append(member.username)
    print("telethon end cycle")
    await client.disconnect()
    print("telethon disconected")
    return chat_members