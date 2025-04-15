from pydantic import BaseModel, ConfigDict


class GroupBaseSchema(BaseModel):
    title: str
    type: str
    owner_id: int
    max_members: int
    current_members: int


class GroupCreateSchema(BaseModel):
    title: str
    max_members: int
    type: str
    owner_id: int


class GroupUpdateSchema(BaseModel):
    title: str | None = None
    max_members: int | None = None


class GroupSchema(GroupBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
