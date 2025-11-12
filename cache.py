import time
import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class MemoryCache:
    """Class for storing cache for timetable

    """

    def __init__(self, main_logger, default_ttl: int = 3600):
        """Initialize MemoryCache
        Args:
            main_logger: Used logger
            default_ttl: ttl time
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.logger = main_logger

    def _get_key(self, group: str, date: str) -> str:
        """Get key
        Args:
            group (str): Group name
            date (str): Date

        Returns:
            str: key for group
        """

        return f"{group}_{date}"

    def get(self, group: str, date: str) -> Optional[Any]:
        """

        Args:
            group:
            date:

        Returns:

        """

        key = self._get_key(group, date)

        if key in self._cache:
            data = self._cache[key]
            if time.time() < data['expires_at']:
                self.logger.debug(f"Кэш HIT для {key}")
                return data['value']
            else:
                # Удаляем просроченные данные
                del self._cache[key]
                self.logger.debug(f"Кэш EXPIRED для {key}")

        self.logger.debug(f"Кэш MISS для {key}")
        return None

    def set(self, group: str, date: str, value: Any, ttl: Optional[int] = None):

        key = self._get_key(group, date)
        ttl = ttl or self.default_ttl

        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }

        self.logger.debug(f"Кэш SET для {key} с TTL {ttl}с")

    def delete(self, group: str, date: str):

        key = self._get_key(group, date)
        if key in self._cache:
            del self._cache[key]
            self.logger.debug(f"Кэш DELETE для {key}")

    def clear_expired(self):

        current_time = time.time()
        expired_keys = [
            key for key, data in self._cache.items()
            if current_time >= data['expires_at']
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self.logger.debug(f"Очищено {len(expired_keys)} просроченных записей")

    def get_stats(self) -> Dict[str, Any]:

        current_time = time.time()
        valid_entries = sum(1 for data in self._cache.values()
                            if current_time < data['expires_at'])

        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self._cache) - valid_entries,
            'memory_size': sum(len(str(v)) for v in self._cache.values())
        }