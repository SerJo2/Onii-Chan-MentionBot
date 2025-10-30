import asyncio
import datetime
import re

import pytz
from festutimetable import TimetableService
from festutimetable.FestuApi import DateNotFoundError, GroupNotFoundError

from config import BotConfing
from main import BotCore


class TimetableHandler:
    def __init__(self):
        self.config = BotConfing.from_env()
        self.timezone = self.config.TIMEZONE

    async def get_timetable_for_day(self, group, date):
        try:
            loop = asyncio.get_event_loop()
            festu_service = TimetableService()

            timetable = await loop.run_in_executor(
                None,
                festu_service.get_timetable_by_day,
                group,
                date
            )
            return self._format_timetable(timetable)

        except DateNotFoundError:
            return f"📅 Расписание на {date} не найдено"
        except GroupNotFoundError:
            return "❌ Группа не найдена. Проверьте правильность написания."
        except Exception as e:
            return "⚠️ Произошла ошибка при получении расписания"

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