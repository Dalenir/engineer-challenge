# tests/integration/test_refresh_handler.py
import pytest
from unittest.mock import AsyncMock

from app.commands.refresh_token import RefreshHandler
from domain.entities import User
from domain.services import TokenService
from domain.v_objects import TokenType


@pytest.mark.asyncio
async def test_refresh_token_rotation_logic(active_user_entity: User, token_service: TokenService):
    cache = AsyncMock()
    repo = AsyncMock()
    repo.get_by_id.return_value = active_user_entity

    handler = RefreshHandler(user_repo=repo, token_service=token_service, cache=cache)

    old_refresh_str = token_service.create_token(active_user_entity, TokenType.REFRESH, 77)
    cache.get.return_value = old_refresh_str

    new_tokens = await handler.execute(old_refresh_str)

    # 1. New token passed to cache
    cache.cache.assert_called_once()
    new_refresh_val = cache.cache.call_args[0][1]
    assert new_refresh_val != old_refresh_str

    # 2. Both tokens are returned
    assert new_tokens.access is not None
    assert new_tokens.refresh is not None

    # 3. New refresh token is not the same
    assert new_tokens.refresh != old_refresh_str
