from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date


class ProfileBaseSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None
    user_id: int
    bio: str | None = None
    country: str | None = None
    city: str | None = None
    job: str | None = None
    phone_number: str | None = None


class ProfileUpdateSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    bio: str | None = None
    country: str | None = None
    city: str | None = None
    job: str | None = None
    phone_number: str | None = None


class ProfileSchema(ProfileBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
