from functools import wraps

from sqlalchemy import MetaData, AsyncAdaptedQueuePool, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import sys

class EngineState:
    maker: async_sessionmaker[AsyncSession] | None = None

Base = declarative_base(
    metadata=MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
    )
)


def provide_session(method):
    @wraps(method)
    async def wrapper(*args, **kwargs):
        if kwargs.get("session"):
            return await method(*args, **kwargs)

        maker = getattr(sys, "_sqlalchemy_maker", None)

        if not maker:
            raise RuntimeError("Base is not initialized!")

        async with maker() as session:
            try:
                res = await method(*args, **kwargs, session=session)
                await session.commit()
                return res
            except Exception:
                await session.rollback()
                raise

    return wrapper

def create_sessionmaker(postgres_url: str, pool: bool = True):
    engine = create_async_engine(postgres_url, poolclass=AsyncAdaptedQueuePool if pool else NullPool)
    maker = async_sessionmaker(
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    )
    sys._sqlalchemy_maker = maker
    return maker
