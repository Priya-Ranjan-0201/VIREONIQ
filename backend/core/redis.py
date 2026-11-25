import time
import redis.asyncio as redis
import structlog

from core.config import settings

logger = structlog.get_logger("vireoniq.redis")


class SafeRedis:
    """Async Redis wrapper with TTL-aware in-memory fallback and timed reconnect cooldown."""

    def __init__(self, url: str, retry_cooldown_seconds: float = 30.0):
        self._url = url
        self._client = None
        self._fallback_store = {}
        self._fallback_expiry = {}
        self._disabled_until: float = 0.0
        self._retry_cooldown = retry_cooldown_seconds
        try:
            self._client = redis.from_url(
                url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
            logger.info("redis_client_initialized")
        except Exception as e:
            logger.warning("redis_init_failed", error=str(e), fallback="in_memory")
            self._disabled_until = time.monotonic() + self._retry_cooldown

    @property
    def _is_temporarily_disabled(self) -> bool:
        if self._client is None:
            return True
        if self._disabled_until <= 0.0:
            return False
        if time.monotonic() >= self._disabled_until:
            self._disabled_until = 0.0
            return False
        return True

    def _trip_circuit(self, operation: str, err: Exception) -> None:
        logger.warning(
            "redis_operation_failed",
            operation=operation,
            error=str(err),
            retry_in_seconds=self._retry_cooldown,
        )
        self._disabled_until = time.monotonic() + self._retry_cooldown

    def _purge_if_expired(self, name: str) -> None:
        exp = self._fallback_expiry.get(name)
        if exp is not None and time.monotonic() >= exp:
            self._fallback_store.pop(name, None)
            self._fallback_expiry.pop(name, None)

    async def get(self, name: str):
        self._purge_if_expired(name)
        if self._is_temporarily_disabled:
            return self._fallback_store.get(name)
        try:
            return await self._client.get(name)
        except Exception as e:
            self._trip_circuit("get", e)
            return self._fallback_store.get(name)

    async def set(self, name: str, value: str, *args, **kwargs):
        ex = kwargs.get("ex")
        if not self._is_temporarily_disabled:
            try:
                return await self._client.set(name, value, *args, **kwargs)
            except Exception as e:
                self._trip_circuit("set", e)
        self._fallback_store[name] = str(value)
        if isinstance(ex, (int, float)) and ex > 0:
            self._fallback_expiry[name] = time.monotonic() + float(ex)
        else:
            self._fallback_expiry.pop(name, None)
        return True

    async def setex(self, name: str, time_sec: int, value: str):
        if not self._is_temporarily_disabled:
            try:
                return await self._client.setex(name, time_sec, value)
            except Exception as e:
                self._trip_circuit("setex", e)
        self._fallback_store[name] = str(value)
        if time_sec > 0:
            self._fallback_expiry[name] = time.monotonic() + float(time_sec)
        else:
            self._fallback_store.pop(name, None)
            self._fallback_expiry.pop(name, None)
        return True

    async def delete(self, *names):
        if not self._is_temporarily_disabled:
            try:
                return await self._client.delete(*names)
            except Exception as e:
                self._trip_circuit("delete", e)
        count = 0
        for name in names:
            if name in self._fallback_store:
                del self._fallback_store[name]
                count += 1
            self._fallback_expiry.pop(name, None)
        return count

    async def hset(self, name: str, key: str = None, value: str = None, mapping: dict = None):
        if not self._is_temporarily_disabled:
            try:
                return await self._client.hset(name, key=key, value=value, mapping=mapping)
            except Exception as e:
                self._trip_circuit("hset", e)
        self._purge_if_expired(name)
        if not isinstance(self._fallback_store.get(name), dict):
            self._fallback_store[name] = {}
        if mapping:
            for k, v in mapping.items():
                self._fallback_store[name][str(k)] = str(v)
        elif key is not None:
            self._fallback_store[name][str(key)] = str(value)
        return len(mapping) if mapping else 1

    async def hgetall(self, name: str):
        self._purge_if_expired(name)
        if not self._is_temporarily_disabled:
            try:
                return await self._client.hgetall(name)
            except Exception as e:
                self._trip_circuit("hgetall", e)
        val = self._fallback_store.get(name, {})
        return dict(val) if isinstance(val, dict) else {}

    async def hget(self, name: str, key: str):
        self._purge_if_expired(name)
        if not self._is_temporarily_disabled:
            try:
                return await self._client.hget(name, key)
            except Exception as e:
                self._trip_circuit("hget", e)
        val = self._fallback_store.get(name, {})
        return val.get(key) if isinstance(val, dict) else None

    async def expire(self, name: str, time_sec: int):
        if not self._is_temporarily_disabled:
            try:
                return await self._client.expire(name, time_sec)
            except Exception as e:
                self._trip_circuit("expire", e)
        if name in self._fallback_store:
            if time_sec > 0:
                self._fallback_expiry[name] = time.monotonic() + float(time_sec)
            else:
                self._fallback_store.pop(name, None)
                self._fallback_expiry.pop(name, None)
        return True

    async def ping(self) -> bool:
        if self._is_temporarily_disabled:
            return False
        try:
            return bool(await self._client.ping())
        except Exception as e:
            self._trip_circuit("ping", e)
            return False

    def __getattr__(self, item):
        if self._client:
            return getattr(self._client, item)
        return lambda *args, **kwargs: None


redis_client = SafeRedis(settings.REDIS_URL)
