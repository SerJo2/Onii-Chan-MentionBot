import asyncio
import datetime
import re
from venv import logger

import pytz
from festutimetable import TimetableService
from festutimetable.FestuApi import DateNotFoundError, GroupNotFoundError

from cache import MemoryCache
from config import BotConfing
from main import BotCore


class TimetableHandler:
    def __init__(self, main_logger, cache_ttl=3600):
        self.config = BotConfing.from_env()
        self.timezone = self.config.TIMEZONE
        self.logger = main_logger

        self.cache = MemoryCache(default_ttl=cache_ttl)

        self._start_cache_cleanup()

    def _start_cache_cleanup(self):

        async def cleanup_task():
            while True:
                await asyncio.sleep(300)  # Каждые 5 минут
                self.cache.clear_expired()
                stats = self.cache.get_stats()
                self.logger.debug(f"Статистика кэша: {stats}")

        asyncio.create_task(cleanup_task())

    async def get_timetable_for_day(self, group, date):
        try:

            cached_result = self.cache.get(group, date)
            if cached_result is not None:
                self.logger.info(f"Используем кэшированное расписание для {group} на {date}")
                return cached_result


            self.logger.info(f"Запрос расписания для {group} на {date} (кэш промах)")

            loop = asyncio.get_event_loop()
            festu_service = TimetableService()

            timetable = await loop.run_in_executor(
                None,
                festu_service.get_timetable_by_day,
                group,
                date
            )

            # Форматируем результат
            formatted_result = self._format_timetable(timetable)

            # Сохраняем в кэш
            self.cache.set(group, date, formatted_result)

            return formatted_result

        except DateNotFoundError:
            error_msg = f"📅 Расписание на {date} не найдено"
            self.cache.set(group, date, error_msg, ttl=300)  # Кэшируем ошибку на 5 минут
            return error_msg
        except GroupNotFoundError:
            error_msg = "❌ Группа не найдена. Проверьте правильность написания."
            self.cache.set(group, date, error_msg, ttl=300)  # Кэшируем ошибку на 5 минут
            return error_msg
        except Exception as e:
            self.logger.error(f"Ошибка получения расписания: {e}")
            error_msg = "⚠️ Произошла ошибка при получении расписания"
            self.cache.set(group, date, error_msg, ttl=60)  # Кэшируем ошибку на 1 минуту
            return error_msg

    def _format_timetable(self, timetable):
        if not timetable.lectures:
            return f"📅 {timetable.date}: Вроде пар нету"

        lines = [f"📅 Расписание на {timetable.date}", ""]

        for i, lecture in enumerate(timetable.lectures, 1):
            lines.extend([
                f"🕐 {lecture.time}",
                f"📚 {self._clean_text(lecture.name)}",
            ])

            if lecture.teacher:
                lines.append(f"👨‍🏫 {lecture.teacher}")

            if lecture.classroom:
                lines.append(f"🏫 {lecture.classroom}")

            if i < len(timetable.lectures):
                lines.append("─" * 20)

        return "\n".join(lines)

    def _clean_text(self, text):
        return re.sub(r'[^а-яА-Я0-9ёЁ ()]', '', text)

    async def get_dates(self) -> tuple[str, str]:
        """Получить сегодняшнюю и завтрашнюю дату"""
        now = datetime.datetime.now(pytz.timezone(self.timezone))
        today = now.strftime('%d.%m.%Y')
        tomorrow = (now + datetime.timedelta(days=1)).strftime('%d.%m.%Y')
        return today, tomorrow

    async def clear_cache(self, group: str = None, date: str = None):
        """Очистить кэш (опционально для конкретной группы/даты)"""
        if group and date:
            self.cache.delete(group, date)
            self.logger.info(f"Очищен кэш для {group} на {date}")
        elif group:
            # Очищаем все даты для группы
            today, tomorrow = self.get_dates()
            self.cache.delete(group, today)
            self.cache.delete(group, tomorrow)
            self.logger.info(f"Очищен кэш для группы {group}")
        else:
            # Очищаем весь кэш
            self.cache._cache.clear()
            self.logger.info("Полностью очищен кэш расписаний")

    async def get_cache_stats(self) -> dict:
        """Получить статистику кэша"""
        return self.cache.get_stats()