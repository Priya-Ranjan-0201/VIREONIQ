import redis.asyncio as redis
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class SafeRedis:
    def __init__(self, url: str):
        self._url = url
        self._client = None
        self._fallback_store = {}
        self._disabled = False
        try:
            self._client = redis.from_url(url, encoding="utf-8", decode_responses=True)
            logger.info("Initialized Redis client")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}. Falling back to in-memory store.")
            self._disabled = True

    async def get(self, name: str):
        if self._disabled:
            return self._fallback_store.get(name)
        try:
            return await self._client.get(name)
        except Exception as e:
            logger.warning(f"Redis get failed: {e}. Using in-memory fallback.")
            self._disabled = True
            return self._fallback_store.get(name)

    async def set(self, name: str, value: str, *args, **kwargs):
        if self._disabled:
            self._fallback_store[name] = str(value)
            return True
        try:
            return await self._client.set(name, value, *args, **kwargs)
        except Exception as e:
            logger.warning(f"Redis set failed: {e}. Using in-memory fallback.")
            self._disabled = True
            self._fallback_store[name] = str(value)
            return True

    async def setex(self, name: str, time: int, value: str):
        if self._disabled:
            self._fallback_store[name] = str(value)
            return True
        try:
            return await self._client.setex(name, time, value)
        except Exception as e:
            logger.warning(f"Redis setex failed: {e}. Using in-memory fallback.")
            self._disabled = True
            self._fallback_store[name] = str(value)
            return True

    async def delete(self, *names):
        if self._disabled:
            count = 0
            for name in names:
                if name in self._fallback_store:
                    del self._fallback_store[name]
                    count += 1
            return count
        try:
            return await self._client.delete(*names)
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}. Using in-memory fallback.")
            self._disabled = True
            count = 0
            for name in names:
                if name in self._fallback_store:
                    del self._fallback_store[name]
                    count += 1
            return count

    async def hset(self, name: str, key: str = None, value: str = None, mapping: dict = None):
        if self._disabled:
            if name not in self._fallback_store:
                self._fallback_store[name] = {}
            if not isinstance(self._fallback_store[name], dict):
                self._fallback_store[name] = {}
            if mapping:
                for k, v in mapping.items():
                    self._fallback_store[name][str(k)] = str(v)
            elif key:
                self._fallback_store[name][str(key)] = str(value)
            return len(mapping) if mapping else 1
        try:
            return await self._client.hset(name, key=key, value=value, mapping=mapping)
        except Exception as e:
            logger.warning(f"Redis hset failed: {e}. Using in-memory fallback.")
            self._disabled = True
            if name not in self._fallback_store:
                self._fallback_store[name] = {}
            if not isinstance(self._fallback_store[name], dict):
                self._fallback_store[name] = {}
            if mapping:
                for k, v in mapping.items():
                    self._fallback_store[name][str(k)] = str(v)
            elif key:
                self._fallback_store[name][str(key)] = str(value)
            return len(mapping) if mapping else 1

    async def hgetall(self, name: str):
        if self._disabled:
            val = self._fallback_store.get(name, {})
            return dict(val) if isinstance(val, dict) else {}
        try:
            return await self._client.hgetall(name)
        except Exception as e:
            logger.warning(f"Redis hgetall failed: {e}. Using in-memory fallback.")
            self._disabled = True
            val = self._fallback_store.get(name, {})
            return dict(val) if isinstance(val, dict) else {}

    async def hget(self, name: str, key: str):
        if self._disabled:
            val = self._fallback_store.get(name, {})
            if isinstance(val, dict):
                return val.get(key)
            return None
        try:
            return await self._client.hget(name, key)
        except Exception as e:
            logger.warning(f"Redis hget failed: {e}. Using in-memory fallback.")
            self._disabled = True
            val = self._fallback_store.get(name, {})
            if isinstance(val, dict):
                return val.get(key)
            return None

    async def expire(self, name: str, time: int):
        if self._disabled:
            return True
        try:
            return await self._client.expire(name, time)
        except Exception as e:
            logger.warning(f"Redis expire failed: {e}. Using in-memory fallback.")
            self._disabled = True
            return True

    def __getattr__(self, item):
        if self._client:
            return getattr(self._client, item)
        return lambda *args, **kwargs: None

redis_client = SafeRedis(settings.REDIS_URL)
