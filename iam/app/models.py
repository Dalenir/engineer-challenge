from pydantic import BaseModel, EmailStr

from domain.v_objects import SecurityToken


class MinimalUser(BaseModel):
    email: EmailStr
    password: str

class ResetDataRequest(BaseModel):
    email: EmailStr

class ConfirmResetData(BaseModel):
    token: str
    new_password: str

class AuthTokens(BaseModel):
    access: str
    refresh: str

class UserData(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
