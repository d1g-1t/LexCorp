from __future__ import annotations

from typing import Any

import orjson
from redis.asyncio import Redis


class RedisCache:
    """Thin async JSON cache wrapper around redis-py."""

    def __init__(self, redis_url: str) -> None:
        self._redis: Redis = Redis.from_url(redis_url, decode_responses=False)  # type: ignore[type-arg]

    async def get_json(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return orjson.loads(raw)

    async def set_json(self, key: str, value: Any, *, ttl: int = 900) -> None:
        await self._redis.set(key, orjson.dumps(value), ex=ttl)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def ping(self) -> bool:
        return bool(await self._redis.ping())

    async def close(self) -> None:
        await self._redis.aclose()
