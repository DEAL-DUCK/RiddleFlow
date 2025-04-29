import enum

from pydantic import BaseModel, ConfigDict, model_validator
from enum import Enum
from pydantic import BaseModel, field_validator, constr, conint
from typing import Optional

class GroupStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BANNED = "BANNED"


class GroupBaseSchema(BaseModel):
    title: str
    type: str
    owner_id: int
    description: str
    max_members: int
    current_members: int
    status: GroupStatus
    logo_url: str
    social_media_links: str


class GroupType(str, Enum):
    TEAM = "TEAM"
    JURY = "JURY"


class GroupCreateSchema(BaseModel):
    title: constr(min_length=1, max_length=20)
    max_members: conint(ge=2)
    type: str
    # logo_url: str | None = None
    description: Optional[constr(min_length=1, max_length=200)] = None
    social_media_links: Optional[str] = None

    @field_validator('type')
    def validate_group_type(cls, v):
        try:
            return GroupType[v.upper()]
        except KeyError:
            allowed_values = [e.value for e in GroupType]
            raise ValueError(
                f"Invalid group type. Must be one of: {allowed_values}"
            )

    @model_validator(mode="before")
    def check_max_participants(cls, values):
        max_members = values.get("max_members")
        if max_members is not None and max_members <= 0:
            raise ValueError("max_members must be greater than zero")
        return values


class GroupUpdateSchema(BaseModel):
    title: Optional[constr(min_length=1, max_length=20)] = None
    max_members: Optional[conint(ge=2)] = None
    description: Optional[constr(min_length=1, max_length=200)] = None
    social_media_links: Optional[str] = None
    # logo_url: str | None = None
class GroupSchema(GroupBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
