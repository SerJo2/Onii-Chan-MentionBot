from telebot import types, logger
from telebot.async_telebot import AsyncTeleBot
from config import BotConfing
from telethon_service import TelethonService
from storage import GroupPreferences
from timetable_handler import TimetableHandler
from logger import base_logger

class TelebotCoreService:

    def __init__(self, main_logger):
        self.logger = main_logger
        self.config = BotConfing.from_env()
        self.bot = AsyncTeleBot(self.config.API_TOKEN)
        self.telethon_bot = TelethonService(self.config.API_ID, self.config.API_HASH, self.config.API_TOKEN, self.logger)
        self.group_storage = GroupPreferences(self.logger)
        self.timetable_service = TimetableHandler(self.logger)


    async def run(self):
        self.logger.info("Запуск бота...")
        try:
            # Подключаем Telethon
            await self.telethon_bot.connect()

            # Запускаем бота
            await self.bot.polling()

        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
            raise
        finally:
            # Всегда отключаем Telethon при завершении
            await self.telethon_bot.disconnect()

        self.logger.info("Bot started up")

    async def handle_text_message(self, message):
        self.logger.info("Bot handled text message: " + message.text + " chat.id and thread: " + str(message.chat.id) + " from " + f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name)
        try:
            message_thread_id = self._get_message_thread_id(message)

            command_handlers = {
                "/all": self._handle_all_command,
                "/ping": self._handle_ping_command,
                "/ochelp": self._handle_help_command,
                "/prefs": self._handle_prefs_command,
                "/tt": self._handle_timetable_command,
            }

            clean_command = message.text.split('@')[0] if '@' in message.text else message.text

            if clean_command in command_handlers:
                await command_handlers[clean_command](message, message_thread_id)
            elif message.reply_to_message:
                await self._handle_reply(message, message_thread_id)

        except:
            self.logger.error("Handle text message error")
            raise

    def _get_message_thread_id(self, message):
        try:
            print(message.reply_to_message.message_thread_id)
            return message.reply_to_message.message_thread_id
        except AttributeError:
            return "General"

    async def _handle_all_command(self, message, message_thread_id):
        chat_members = await self.telethon_bot.get_chat_members(message.chat.id)
        print(chat_members)
        chat_members = await self.telethon_bot.get_chat_members(message.chat.id)
        for i in range(0, len(chat_members), 5):
            group = chat_members[i:i + 5]
            send = ""
            for j in group:
                k = "@" + j
                send = send + k + " "
            await self.bot.send_message(message.chat.id, send, message_thread_id=message_thread_id)

    async def _handle_ping_command(self, message, message_thread_id):
        await self.bot.send_message(message.chat.id, "Бот в порядке", message_thread_id=message_thread_id)

    async def _handle_help_command(self, message, message_thread_id):
        help_text = """
🤖 Доступные команды:

/all - Упоминание всех участников
/ping - Проверка работы бота  
/prefs - Настройка группы
/tt - Получить расписание
/ochelp - Справка по командам
                """
        await self.bot.send_message(message.chat.id, help_text.strip(), message_thread_id=message_thread_id)

    async def handle_callback(self, call):
        message_thread_id = self._get_message_thread_id(call.message)
        try:
            if str(call.message.chat.id) not in await self.group_storage.load():
                await self.bot.send_message(
                    call.message.chat.id,
                    "❌ Группа не настроена. Используйте /prefs для настройки",
                    message_thread_id=message_thread_id
                )
                return

            group_name = await self.group_storage.get_group(str(call.message.chat.id))
            today, tomorrow = await self.timetable_service.get_dates()

            if call.data == 'today':
                timetable_text = await self.timetable_service.get_timetable_for_day(group_name, today)
            elif call.data == 'tomorrow':
                timetable_text = await self.timetable_service.get_timetable_for_day(group_name, tomorrow)
            else:
                return

            # Добавляем упоминание пользователя
            user_mention = f"@{call.from_user.username}" if call.from_user.username else call.from_user.first_name
            response = f"{user_mention}\n\n{timetable_text}"

            await self.bot.send_message(
                call.message.chat.id,
                response,
                message_thread_id=message_thread_id
            )

        except Exception as e:
            self.logger.error("Callback handle error: ", str(e))
            await self._handle_error(e, call.message, message_thread_id)


    async def _handle_prefs_command(self, message, message_thread_id):
        await self.bot.send_message(
            message.chat.id,
            "✏️ Ответьте на это сообщение названием группы, например: БО911ПИА",
            message_thread_id=message_thread_id,
            reply_to_message_id=message.message_id
        )

    async def _handle_timetable_command(self, message, message_thread_id):
        markup = types.InlineKeyboardMarkup()
        today_btn = types.InlineKeyboardButton("📅 Сегодня", callback_data='today')
        tomorrow_btn = types.InlineKeyboardButton("📆 Завтра", callback_data='tomorrow')
        markup.add(today_btn, tomorrow_btn)

        await self.bot.send_message(
            message.chat.id,
            "📚 Выберите дату:",
            reply_markup=markup,
            message_thread_id=message_thread_id
        )

    async def _handle_reply(self, message, message_thread_id):
        if (message.reply_to_message and
                message.reply_to_message.text == "✏️ Ответьте на это сообщение названием группы, например: БО911ПИА"):
            await self.group_storage.set_group(message.chat.id, message.text)
            await self.bot.send_message(
                message.chat.id,
                f"✅ Группа установлена: {message.text.upper()}",
                message_thread_id=message_thread_id
            )

    async def _handle_error(self, error, message, message_thread_id):
        await self.bot.send_message(
            message.chat.id,
            f"❌ Произошла ошибка: {str(error)}\n\n📞 Свяжитесь с @psibladeabuzerz",
            message_thread_id=message_thread_id
        )


