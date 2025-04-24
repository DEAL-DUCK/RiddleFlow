from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, validator, model_validator, constr, field_validator
from datetime import date
import phonenumbers

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
    first_name: Optional[constr(min_length=1, max_length=20)] = None
    last_name: Optional[constr(min_length=1, max_length=20)] = None
    bio: str | None = None
    country: str | None = None
    city: str | None = None
    job: str | None = None
    phone_number: str | None = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            parsed = phonenumbers.parse(v, cls.country if hasattr(cls, 'country') else None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format')


class ProfileSchema(ProfileBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
