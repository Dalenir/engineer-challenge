from dataclasses import dataclass

from .v_objects import Email, PasswordHash


@dataclass
class User:
    email: Email
    password_hash: PasswordHash
    id: str = None
    is_active: bool = True

    def validate_password(self, password: str, hasher):
        return hasher.verify(password, self.password_hash)
