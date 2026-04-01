from app.interfaces import CacheService
from app.models import AuthTokens
from domain.entities import User
from domain.policies import TokenLifetimePolicy
from domain.services import TokenService
from domain.v_objects import TokenType


async def create_and_cache_token_pair(user: User, token_service: TokenService, cache_service: CacheService) -> AuthTokens:
    new_access = token_service.create_token(
        user, TokenType.ACCESS, TokenLifetimePolicy.get_ttl(TokenType.ACCESS)
    )
    ttl_refresh = TokenLifetimePolicy.get_ttl(TokenType.REFRESH)
    new_refresh = token_service.create_token(user, TokenType.REFRESH, ttl_refresh)

    await cache_service.cache(f"refresh:{user.id}", new_refresh, expire=ttl_refresh)
    return AuthTokens(
        access=new_access,
        refresh=new_refresh
    )