import asyncio
from threading import main_thread

import telebot_core_service
from logger import base_logger

class BotCore:
    def __init__(self, main_logger: base_logger):
        self.logger = main_logger
        self.telebot_service = telebot_core_service.TelebotCoreService(self.logger)
        self._register_handlers()


    def _register_handlers(self):
        """Регистрация обработчиков"""
        self.telebot_service.bot.message_handler(content_types=['text'])(self.telebot_service.handle_text_message)
        self.telebot_service.bot.callback_query_handler(func=lambda call: True)(self.telebot_service.handle_callback)


    async def run(self):
        await self.telebot_service.run()


async def main():
    main_logger = base_logger('Onii-Chan', 'Onii-Chan.log')
    bot = BotCore(main_logger)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())



