import enum

from pydantic import BaseModel, ConfigDict


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


class GroupCreateSchema(BaseModel):
    title: str
    max_members: int
    type: str
    description: str | None = None
    logo_url: str | None = None
    social_media_links: str | None = None


class GroupUpdateSchema(BaseModel):
    title: str | None = None
    max_members: int | None = None
    description: str | None = None
    logo_url: str | None = None
    social_media_links: str | None = None


class GroupSchema(GroupBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
