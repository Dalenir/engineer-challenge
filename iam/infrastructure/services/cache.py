import json
from datetime import timedelta
from typing import Any

from app.interfaces import CacheService
from redis import asyncio as aioredis

class RedisCacheService(CacheService):
    def __init__(self, url: str):
        self._client = aioredis.from_url(url, decode_responses=True)

    async def get_dict(self, key: str) -> dict | None:
        data = await self._client.get(key)
        return json.loads(data) if data else None

    async def cache_dict(self, key: str, value: dict, expire: int = 3600) -> None:
        await self._client.set(key, json.dumps(value), ex=expire)

    async def get(self, key: str) -> Any:
        return await self._client.get(key)

    async def cache(self, key: str, value: Any, expire: int = 3600):
        return await self._client.set(key, value, ex=expire)

    async def increment(self, key: str, expire: int) -> int:
        curr = await self._client.incr(key)
        if curr == 1:
            await self._client.expire(key, time=timedelta(seconds=expire))
        return curr
