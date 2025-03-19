from pydantic import BaseModel, ConfigDict


class HackathonBaseSchema(BaseModel):
    name: str
    description: str
    theme: str


class HackathonCreateSchema(HackathonBaseSchema):
    pass


class HackathonSchema(HackathonBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
