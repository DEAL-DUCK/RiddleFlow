from enum import Enum

from pydantic import BaseModel, ConfigDict


class HackathonTaskType(str, Enum):
    CODING = "CODING"
    DESIGN = "DESIGN"
    QA = "QA"
    OTHER = "OTHER"


class CreateHackathonTaskSchema(BaseModel):
    title: str
    description: str
    task_type: HackathonTaskType
    max_attempts: int = 5


class HackathonTaskSchema(BaseModel):
    id: int
    title: str
    description: str
    task_type: HackathonTaskType
    hackathon_id: int

    model_config = ConfigDict(from_attributes=True)


class HackathonTaskUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    task_type: HackathonTaskType | None = None
    hackathon_id: int | None = None
    max_attempts: int = 5
