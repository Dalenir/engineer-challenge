from pydantic import Field, computed_field
from pydantic_settings import BaseSettings


class MainSettings(BaseSettings):
    POST_DNM: str = Field(..., validation_alias="DB_NAME")
    POST_USR: str = Field(..., validation_alias="DB_USERNAME")
    POST_PWD: str = Field(..., validation_alias="DB_PASSWORD")

    SECRET_HASH: str

    @computed_field
    @property
    def postgres_url(self) -> str:
        return f"postgresql+asyncpg://{self.POST_USR}:{self.POST_PWD}@postgres:5432/{self.POST_DNM}?async_fallback=True"

    @property
    def redis_url(self) -> str:
        return f'redis://:@redis:2769'
