from domain.entities import User
from domain.repositories import UserRepository
from domain.services import PasswordService
from domain.v_objects import Email, PasswordHash
from ..models import MinimalUser


class RegisterUserHandler:
    user_repo: UserRepository
    pwd_service: PasswordService

    def __init__(self, user_repo: UserRepository, pwd_service: PasswordService):
        self.user_repo = user_repo
        self.pwd_service = pwd_service

    async def execute(self, user_data: MinimalUser) -> str:
        existing_user = await self.user_repo.get_by_email(Email(user_data.email))
        if existing_user:
            raise ValueError("User already exists")

        hashed_password = self.pwd_service.hash_password(user_data.password)

        new_user = User(
            email=Email(user_data.email),
            password_hash=PasswordHash(hashed_password)
        )

        user_id = await self.user_repo.save(new_user)
        return user_id
