import uuid

from sqlalchemy import String, Column, Boolean, DateTime, func

from ..db import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_domain(self):
        from domain.entities import User
        return User(
            id=self.id,
            email=self.email,
            password_hash=self.password_hash,
            is_active=self.is_active
        )
