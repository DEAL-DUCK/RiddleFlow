from pydantic import BaseModel, ConfigDict


class CreateContestTaskSchema(BaseModel):
    title: str
    description: str
    time_limit: int
    memory_limit: int


class ContestTaskSchema(BaseModel):
    id: int
    title: str
    description: str
    contest_id: int
    time_limit: int
    memory_limit: int
    model_config = ConfigDict(from_attributes=True)


class ContestTaskUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    contest_id: int | None = None
    time_limit: int | None = None
    memory_limit: int | None = None
