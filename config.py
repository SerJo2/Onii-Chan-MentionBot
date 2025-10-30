import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfing:
    API_TOKEN: str
    MY_CHAT_ID: int
    API_ID: int
    API_HASH: str
    TIMEZONE: str = "Asia/Vladivostok"

    @classmethod
    def from_env(cls):
        return cls(
            API_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
            MY_CHAT_ID=int(os.getenv("MY_CHAT_ID")),
            API_ID=int(os.getenv("TELEGRAM_API_ID")),
            API_HASH=os.getenv("TELEGRAM_API_HASH")
        )