import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


@dataclass(frozen=True)
class PasswordHash:
    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 32:
            raise ValueError("PasswordHash: invalid format or too short")

    def __str__(self):
        return self.value

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        clean_value = self.value.strip().lower()
        object.__setattr__(self, "value", clean_value)

        if not self._is_valid(clean_value):
            raise ValueError(f"'{self.value}' is not a valid email address")

    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value

    @property
    def domain(self) -> str:
        """Пример бизнес-логики внутри VO"""
        return self.value.split("@")[-1]


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"

@dataclass(frozen=True)
class SecurityToken:
    value: str
    user_id: UUID
    token_type: TokenType
    expires_at: datetime

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

    def is_reset_token(self) -> bool:
        return self.token_type == TokenType.PASSWORD_RESET
