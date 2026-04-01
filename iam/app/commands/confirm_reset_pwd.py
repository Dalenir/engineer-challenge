from app.commands._shared import create_and_cache_token_pair
from app.interfaces import CacheService
from app.models import ConfirmResetData, AuthTokens
from domain.policies import TokenLifetimePolicy
from domain.repositories import UserRepository
from domain.services import TokenService, PasswordService
from domain.v_objects import TokenType, PasswordHash


class ConfirmResetHandler:

    def __init__(
            self,
            user_repo: UserRepository,
            token_service: TokenService,
            pwd_service: PasswordService,
            cache: CacheService
    ):
        self._user_repo = user_repo
        self._token_service = token_service
        self._pwd_service = pwd_service
        self._cache = cache

    async def execute(self, data: ConfirmResetData) -> AuthTokens:
        token_vo = self._token_service.decode_token(data.token)

        if token_vo.token_type != TokenType.PASSWORD_RESET:
            raise PermissionError("Invalid token type")

        user = await self._user_repo.get_by_id(str(token_vo.user_id))
        if not user:
            raise ValueError("User not found")

        new_password_hash = self._pwd_service.hash_password(data.new_password)
        user.password_hash = PasswordHash(new_password_hash)

        await self._user_repo.save(user)

        return await create_and_cache_token_pair(user, token_service=self._token_service, cache_service=self._cache)
