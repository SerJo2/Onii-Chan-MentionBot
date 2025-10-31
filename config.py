import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class CacheConfig:

    ENABLED: bool = True
    TTL_SECONDS: int = 3600  # 1 час
    USE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379"
    CLEANUP_INTERVAL: int = 300  # 5 минут

@dataclass
class BotConfing:
    API_TOKEN: str
    MY_CHAT_ID: int
    API_ID: int
    API_HASH: str
    TIMEZONE: str = "Asia/Vladivostok"
    LOG_LEVEL: str = "INFO"
    CACHE_CONFIG: CacheConfig = None

    def __post_init__(self):
        if self.CACHE_CONFIG is None:
            self.CACHE_CONFIG = CacheConfig()

    @classmethod
    def from_env(cls):
        return cls(
            API_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
            MY_CHAT_ID=int(os.getenv("MY_CHAT_ID")),
            API_ID=int(os.getenv("TELEGRAM_API_ID")),
            API_HASH=os.getenv("TELEGRAM_API_HASH"),
            CACHE_CONFIG=CacheConfig(
                ENABLED=os.getenv("CACHE_ENABLED", "true").lower() == "true",
                TTL_SECONDS=int(os.getenv("CACHE_TTL", "3600")),
                USE_REDIS=os.getenv("USE_REDIS", "false").lower() == "true",
                REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379")
            )
        )