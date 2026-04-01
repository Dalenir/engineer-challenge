from abc import ABC, abstractmethod

from .entities import User
from .v_objects import Email


class UserRepository(ABC):

    @abstractmethod
    async def save(self, user: User, **kwargs) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, id_: str, **kwargs) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: Email, **kwargs) -> User | None:
        pass