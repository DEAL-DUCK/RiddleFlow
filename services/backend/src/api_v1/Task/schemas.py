from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    CODING = "CODING"
    DESIGN = "DESIGN"
    QA = "QA"
    OTHER = "OTHER"


class CreateTaskSchema(BaseModel):
    title: str
    description: str
    task_type: TaskType



class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    task_type: TaskType
    hackathon_id: int

    model_config = ConfigDict(from_attributes=True)
class TaskUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    task_type: TaskType | None = None
    hackathon_id: int | None = None
