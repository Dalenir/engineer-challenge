from app.commands._shared import create_and_cache_token_pair
from app.interfaces import CacheService
from app.models import AuthTokens
from domain.policies import TokenLifetimePolicy
from domain.repositories import UserRepository
from domain.services import TokenService
from domain.v_objects import TokenType


class RefreshHandler:
    def __init__(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
        cache: CacheService
    ):
        self._user_repo = user_repo
        self._token_service = token_service
        self._cache = cache

    async def execute(self, refresh_token: str) -> AuthTokens:
        token_vo = self._token_service.decode_token(refresh_token)

        if token_vo.token_type != TokenType.REFRESH:
            raise PermissionError("Invalid token type. Expected REFRESH.")

        refresh_cache_key = f"refresh:{token_vo.user_id}"
        stored_token = await self._cache.get(refresh_cache_key)
        if stored_token != refresh_token:
            raise PermissionError("Token has been revoked or rotated")

        user = await self._user_repo.get_by_id(str(token_vo.user_id))
        if not user or not user.is_active:
            raise ValueError("User is inactive or not found")

        return await create_and_cache_token_pair(user, token_service=self._token_service, cache_service=self._cache)
