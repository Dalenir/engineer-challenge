from uuid import uuid4

import pytest

from domain.entities import User
from domain.v_objects import Email, PasswordHash
from infrastructure.services.security import JWTTokenService


@pytest.fixture
def token_service():
    return JWTTokenService(secret="3"*32, algorithm="HS256")

@pytest.fixture
def user_entity():
    return User(id=str(uuid4()), email=Email("dev@null.com"),
                password_hash=PasswordHash("3"*32))

@pytest.fixture
def active_user_entity():
    return User(
        id=str(uuid4()),
        email=Email("test@example.com"),
        password_hash=PasswordHash("3"*32),
        is_active=True
    )