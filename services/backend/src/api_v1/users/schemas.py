

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from fastapi_users import schemas

from core.types.user_id import UserIdType


"""class UserSchema(BaseModel):
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

"""
class UserUpdate(schemas.BaseUserUpdate):
    username: str

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional
from fastapi_users import schemas
from core.types.user_id import UserIdType





from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import datetime
from enum import Enum
from typing import Optional
from fastapi_users import schemas
from core.types.user_id import UserIdType


class UserRole(str, Enum):
    PARTICIPANT = "PARTICIPANT"
    CREATOR = "CREATOR"


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(..., min_length=3, max_length=40)
    user_role: str = UserRole.PARTICIPANT.value
    class Config:
        extra = "forbid"

    @field_validator('user_role')
    @classmethod
    def validate_user_role(cls, v: str) -> str:
        if v not in [role.value for role in UserRole]:
            raise ValueError(
                f"Invalid role '{v}'. Must be one of: {[role.value for role in UserRole]}"
            )
        return v


class UserRead(schemas.BaseUser[UserIdType]):
    model_config = ConfigDict(from_attributes=True)

    username: str
    email: EmailStr
    user_role: str
    created_at: datetime
    id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    @field_validator('user_role')
    @classmethod
    def validate_user_role(cls, v: str) -> str:
        if v not in [role.value for role in UserRole]:
            raise ValueError(
                f"Invalid role '{v}'. Must be one of: {[role.value for role in UserRole]}"
            )
        return v