from abc import ABC, abstractmethod
from typing import Any, Optional

class CacheService(ABC):

    @abstractmethod
    async def get_dict(self, key: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def cache_dict(self, key: str, value: dict, expire: int = 3600) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> Any:
        pass

    @abstractmethod
    async def cache(self, key: str, value: Any, expire: int = 3600):
        pass

    @abstractmethod
    async def increment(self, key: str, expire: int) -> int:
        pass
