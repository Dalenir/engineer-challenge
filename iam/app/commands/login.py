from dataclasses import asdict

from app.commands._shared import create_and_cache_token_pair
from app.interfaces import CacheService
from app.models import MinimalUser, AuthTokens
from domain.entities import User
from domain.policies import TokenLifetimePolicy
from domain.repositories import UserRepository
from domain.services import PasswordService, TokenService
from domain.v_objects import Email, TokenType


class LoginHandler:

    _pwd_service: PasswordService
    _token_service: TokenService
    _user_repo: UserRepository
    _cache: CacheService

    def __init__(
            self,
            user_repo: UserRepository,
            pwd_service: PasswordService,
            token_service: TokenService,
            cache_service: CacheService
    ):
        self._user_repo = user_repo
        self._pwd_service = pwd_service
        self._token_service = token_service
        self._cache = cache_service

    async def execute(self, user_data: MinimalUser) -> AuthTokens:

        user = await self._user_repo.get_by_email(Email(user_data.email))
        if not user:
            raise PermissionError("Invalid credentials")

        is_valid = self._pwd_service.verify_password(
            user_data.password,
            user.password_hash
        )

        if not is_valid:
            raise PermissionError("Invalid credentials")

        return await create_and_cache_token_pair(user, token_service=self._token_service, cache_service=self._cache)
