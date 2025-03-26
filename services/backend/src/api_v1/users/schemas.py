from pydantic import BaseModel, ConfigDict, EmailStr
import datetime


class UserBaseSchema(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    role: str
    created_at: datetime.datetime


class UserCreateSchema(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    role: str


class UserSchema(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
