from pydantic import BaseModel, ConfigDict


class OlympiadBaseSchema(BaseModel):
    name: str
    description: str
    theme: str


class OlympiadCreateSchema(OlympiadBaseSchema):
    pass


class OlympiadSchema(OlympiadBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
