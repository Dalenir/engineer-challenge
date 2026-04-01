import asyncio
import grpc
import structlog

from app.commands.confirm_reset_pwd import ConfirmResetHandler
from app.commands.refresh_token import RefreshHandler
from app.commands.register import RegisterUserHandler
from app.queries.authenticate import AuthenticateHandler
from app.queries.request_reset_pwd import RequestResetHandler
from app.commands.login import LoginHandler
from config import MainSettings
from infrastructure.postgres.db import create_sessionmaker
from infrastructure.services.cache import RedisCacheService

from presentation.generated import iam_pb2_grpc
from presentation.rate_limit_intc import RateLimitInterceptor
from presentation.servicer import AuthServicer

from infrastructure.postgres.repositories import PostgresUserRepository
from infrastructure.services.security import BcryptPasswordService, JWTTokenService

def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()

settings = MainSettings()   # noqa

async def serve():

    create_sessionmaker(settings.postgres_url)
    redis_cache = RedisCacheService(settings.redis_url)

    user_repo = PostgresUserRepository()
    password_service = BcryptPasswordService()
    token_service = JWTTokenService(secret=settings.SECRET_HASH)

    register_handler = RegisterUserHandler(user_repo, password_service)
    reset_password_handler = RequestResetHandler(user_repo, token_service)
    confirm_reset_password_handler = ConfirmResetHandler(user_repo, token_service, password_service, cache=redis_cache)
    refresh_handler = RefreshHandler(user_repo, token_service, redis_cache)
    auth_handler = AuthenticateHandler(user_repo, token_service, redis_cache)

    login_handler = LoginHandler(user_repo, password_service, token_service, redis_cache)

    auth_servicer = AuthServicer(
        register_handler=register_handler,
        login_handler=login_handler,
        request_reset_handler=reset_password_handler,
        confirm_reset_handler=confirm_reset_password_handler,
        refresh_handler=refresh_handler,
        authenticate_handler=auth_handler
    )

    rl_interceptor = RateLimitInterceptor(cache_service=redis_cache)
    # lg_interceptor = LoggingInterceptor()

    server = grpc.aio.server(interceptors=[rl_interceptor])
    iam_pb2_grpc.add_AuthServiceServicer_to_server(auth_servicer, server)

    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)

    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("Stopping server...")
        await server.stop(5)

if __name__ == "__main__":
    asyncio.run(serve())
