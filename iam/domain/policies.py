from datetime import timedelta

from .v_objects import TokenType


class TokenLifetimePolicy:
    @staticmethod
    def get_ttl(token_type: TokenType) -> int:
        match token_type:
            case TokenType.ACCESS: return int(timedelta(minutes=10).total_seconds())
            case TokenType.REFRESH: return int(timedelta(days=7).total_seconds())
            case TokenType.PASSWORD_RESET: return int(timedelta(minutes=20).total_seconds())
