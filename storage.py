import datetime
import json
import aiofiles
from typing import Dict, Any
from pathlib import Path
from config import BotConfing
import pytz


class GroupPreferences:

    def __init__(self, file_path: str = "data.json"):
        self.file_path = Path(file_path)

    async def load(self) -> Dict[int, str]:
        try:
            async with aiofiles.open(self.file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def save(self, data: Dict[int, str]):
        async with aiofiles.open(self.file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))

    async def get_group(self, chat_id: int | str) -> str:
        prefs = await self.load()
        return prefs.get(chat_id)

    async def set_group(self, chat_id: int, group: str):
        prefs = await self.load()
        prefs[chat_id] = group.upper().replace(' ', '')
        await self.save(prefs)
