from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities import User
from domain.repositories import UserRepository
from domain.v_objects import Email
from ..db import provide_session
from ..models.user import UserModel


class PostgresUserRepository(UserRepository):

    @classmethod
    @provide_session
    async def save(cls, user: User, *, session: AsyncSession = None) -> str:
        session: AsyncSession

        stmt = select(UserModel).where(UserModel.email == str(user.email))
        result = await session.execute(stmt)
        u_user = result.scalar_one_or_none()

        if u_user:
            u_user.email = str(user.email)
            u_user.password_hash = str(user.password_hash)
            u_user.is_active = user.is_active
        else:
            u_user = UserModel(
                id=user.id,
                email=str(user.email),
                password_hash=str(user.password_hash),
                is_active=user.is_active
            )
            session.add(u_user)
        await session.commit()
        await session.refresh(u_user)
        return u_user.id

    @classmethod
    @provide_session
    async def get_by_id(cls, id_: str, *, session: AsyncSession = None) -> User | None:
        session: AsyncSession

        stmt = select(UserModel).where(UserModel.id == id_)
        result = await session.execute(stmt)
        model: UserModel | None = result.scalar_one_or_none()
        return model.to_domain() if model else None

    @classmethod
    @provide_session
    async def get_by_email(cls, email: Email, *, session: AsyncSession = None) -> User | None:
        session: AsyncSession

        stmt = select(UserModel).where(UserModel.email == str(email))
        result = await session.execute(stmt)
        model: UserModel | None = result.scalar_one_or_none()
        return model.to_domain() if model else None
