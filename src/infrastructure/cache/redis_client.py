from __future__ import annotations

from typing import Any

import orjson
from redis.asyncio import Redis


class RedisCache:

    def __init__(self, redis: Redis) -> None:  # type: ignore[type-arg]
        self._redis = redis

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
        return await self._redis.ping()  # type: ignore[return-value]
