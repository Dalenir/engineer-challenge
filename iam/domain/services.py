from abc import abstractmethod, ABC
from typing import Any

from .entities import User
from .v_objects import PasswordHash, TokenType, SecurityToken


class PasswordService(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, password: str, hashed_password: PasswordHash) -> bool:
        pass


class TokenService(ABC):
    @abstractmethod
    def create_token(self, user: User, token_type: TokenType, expires_delta: int) -> str:
        pass

    @abstractmethod
    def create_access_pair(self, user: User, token_type: TokenType, expires_deltas: tuple[int, int]) -> tuple[str, str]:
        """
        Create token pair: tuple[*access_token*, *refresh_token*]
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> SecurityToken:
        pass
