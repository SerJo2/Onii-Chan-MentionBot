import asyncio

import telebot_core_service

class BotCore:
    def __init__(self):
        self.telebot_service = telebot_core_service.TelebotCoreService()

        self._register_handlers()

    def _register_handlers(self):
        """Регистрация обработчиков"""
        self.telebot_service.bot.message_handler(content_types=['text'])(self.telebot_service.handle_text_message)
        self.telebot_service.bot.callback_query_handler(func=lambda call: True)(self.telebot_service.handle_callback)


    async def run(self):
        await self.telebot_service.run()


async def main():
    bot = BotCore()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())



