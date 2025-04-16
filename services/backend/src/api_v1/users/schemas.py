import datetime

from pydantic import BaseModel, ConfigDict, EmailStr
from fastapi_users import schemas

from core.types.user_id import UserIdType


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    hashed_password: str
    email: EmailStr
    user_role: str
    created_at: datetime.datetime
    id: int


class UserRead(schemas.BaseUser[UserIdType]):
    username: str
    user_role: str


class UserCreate(schemas.BaseUserCreate):
    username: str
    user_role: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str
    user_role: str
