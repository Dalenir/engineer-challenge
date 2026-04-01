from dataclasses import asdict

from app.interfaces import CacheService
from app.models import UserData
from domain.entities import User
from domain.repositories import UserRepository
from domain.services import TokenService
from domain.v_objects import TokenType, Email


class AuthenticateHandler:
    _cache: CacheService
    _token_service: TokenService
    _user_repo: UserRepository

    def __init__(
            self,
            user_repo: UserRepository,
            token_service: TokenService,
            cache: CacheService
    ):
        self._user_repo = user_repo
        self._token_service = token_service
        self._cache = cache

    async def execute(self, access_token_str: str) -> UserData:
        token_vo = self._token_service.decode_token(access_token_str)

        if token_vo.token_type != TokenType.ACCESS:
            raise PermissionError("Only ACCESS tokens are allowed for authentication")

        cache_key = f"users:{token_vo.user_id}"
        cached_user = await self._cache.get_dict(cache_key)
        if isinstance(cached_user, dict):
            user = User(**cached_user)
        else:
            user = await self._user_repo.get_by_id(str(token_vo.user_id))

        if user:
            await self._cache.cache_dict(cache_key, asdict(user), expire=300)
        else:
            raise ValueError("User not found")

        if not user.is_active:
            raise PermissionError("User account is disabled")

        return UserData(
            id=user.id,
            email=str(user.email),
            is_active=user.is_active
        )
