from pydantic import BaseModel, ConfigDict


class CreateContestTaskSchema(BaseModel):
    title: str
    description: str


class ContestTaskSchema(BaseModel):
    id: int
    title: str
    description: str
    contest_id: int
    model_config = ConfigDict(from_attributes=True)


class ContestTaskUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    contest_id: int | None = None
