import asyncio
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors import (
    ChatAdminRequiredError,
    ChannelPrivateError,
    FloodWaitError
)
import logging


class TelethonService:
    def __init__(self, api_id, api_hash, api_token, main_logger):
        self.api_id = api_id
        self.api_hash = api_hash
        self.api_token = api_token
        self.logger = main_logger
        self.client = None
        self.is_connected = False

    async def connect(self):
        """Подключение к Telegram"""
        if self.is_connected:
            return

        try:
            self.client = TelegramClient('session_name', self.api_id, self.api_hash)
            await self.client.start(bot_token=self.api_token)
            self.is_connected = True
            self.logger.info("Telethon client connected successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect Telethon client: {e}")
            raise

    async def disconnect(self):
        """Отключение от Telegram"""
        if self.client and self.is_connected:
            await self.client.disconnect()
            self.is_connected = False
            self.logger.info("Telethon client disconnected")

    async def ensure_connected(self):
        """Убедиться, что клиент подключен"""
        self.logger.info("Start ensure_connected")
        if not self.is_connected or not self.client:
            await self.connect()

    async def get_chat_members(self, chat_id):
        """Получить список участников чата"""
        self.logger.info("Start get_chat_members")
        try:
            await self.ensure_connected()

            self.logger.info(f"Getting chat members for chat_id: {chat_id}")
            chat_members = []

            async for member in self.client.iter_participants(chat_id):
                if member.username is not None and not member.bot:
                    chat_members.append(member.username)

            self.logger.info(f"Found {len(chat_members)} chat members")
            return chat_members

        except ChatAdminRequiredError:
            self.logger.error(f"Bot needs admin rights in chat {chat_id}")
            return []
        except ChannelPrivateError:
            self.logger.error(f"Chat {chat_id} is private or inaccessible")
            return []
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait: {e.seconds} seconds")
            return []
        except Exception as e:
            self.logger.error(f"Error getting chat members: {e}")
            return []

    async def __aenter__(self):
        """Контекстный менеджер для использования with"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер для автоматического отключения"""
        await self.disconnect()