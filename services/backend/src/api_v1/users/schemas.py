from pydantic import BaseModel, ConfigDict, EmailStr
import datetime
from enum import Enum

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

class UserRole(str,Enum):
    CREATOR = "CREATOR"
    PARTICIPANT = "PARTICIPANT"
class UserSchema(UserBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
class UserSchema2(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    role : UserRole
    password : bytes
    email: EmailStr | None = None
    active : bool = True
