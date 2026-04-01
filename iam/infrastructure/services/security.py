from datetime import datetime, timezone, timedelta
from uuid import UUID

import bcrypt
import jwt
from jwt import InvalidTokenError

from domain.entities import User
from domain.policies import TokenLifetimePolicy
from domain.services import PasswordService, TokenService
from domain.v_objects import PasswordHash, TokenType, SecurityToken


class BcryptPasswordService(PasswordService):
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, hashed_password: PasswordHash) -> bool:
        return bcrypt.checkpw(password.encode(), str(hashed_password).encode())


class JWTTokenService(TokenService):

    def __init__(self, secret: str, algorithm: str = "HS256"):
        self._secret = secret
        self._algo = algorithm

    def create_token(self, user: User, token_type: TokenType, expires_delta: int = 3600) -> str:
        expires_at = datetime.now() + timedelta(seconds=expires_delta)

        payload = {
            "sub": str(user.id),
            "email": str(user.email),
            "type": token_type.value,
            "exp": expires_at
        }

        token_string = jwt.encode(payload, self._secret, algorithm=self._algo)
        return token_string

    def decode_token(self, token: str) -> SecurityToken:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algo])

            return SecurityToken(
                value=token,
                user_id=UUID(payload["sub"]),
                token_type=TokenType(payload["type"]),
                expires_at=datetime.fromtimestamp(payload["exp"])
            )
        except (jwt.PyJWTError, KeyError, ValueError) as e:
            raise InvalidTokenError(f"Token is invalid or expired: {str(e)}")

    def create_access_pair(self, user: User,
                           token_type: TokenType, base_expire_delta: int
                           ) -> tuple[str, str]:
        return self.create_token(user, TokenType.ACCESS, base_expire_delta), self.create_token(user, TokenType.REFRESH, base_expire_delta*10)
