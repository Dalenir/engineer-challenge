import structlog

from domain.v_objects import Email, TokenType
from app.models import ResetDataRequest
from domain.repositories import UserRepository
from domain.services import TokenService

logging = structlog.get_logger()

class RequestResetHandler:
    def __init__(self, user_repo: UserRepository, token_service: TokenService):
        self._user_repo = user_repo
        self._token_service = token_service

    async def execute(self, data: ResetDataRequest) -> str:
        user = await self._user_repo.get_by_email(Email(data.email))

        if user:
            reset_token = self._token_service.create_token(user, TokenType.PASSWORD_RESET, expires_delta=1200)

            logging.info(reset_token)   # Instead of real email sending

        return "Check your email"
