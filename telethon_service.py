from telethon import TelegramClient


class TelethonService:
    def __init__(self, api_id, api_hash):
        self.telethon_client = TelegramClient('session_name', api_id, api_hash)


    async def run(self):
        await self.telethon_client.run_until_disconnected()

    async def disconnect(self):
        await self.telethon_client.disconnect()

    async def get_chat_members(self, chat_id):
        chat_members = []
        async for member in self.telethon_client.iter_participants(chat_id):
            if member.username is not None:
                chat_members.append(member.username)
        return chat_members