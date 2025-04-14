import datetime

from pydantic import BaseModel, ConfigDict, EmailStr
from fastapi_users import schemas

from core.types.user_id import UserIdType


class UserBaseSchema(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    user_role: str
    created_at: datetime.datetime


class UserCreateSchema(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    user_role: str


class UserSchema(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)
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
