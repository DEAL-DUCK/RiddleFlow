from pydantic import BaseModel, ConfigDict
import datetime

# import enum
#
# class HackathonStatus(enum.Enum):
#     PLANNED = "planned"
#     ACTIVE = "active"
#     COMPLETED = "completed"
#     CANCELED = "canceled"


class HackathonBaseSchema(BaseModel):
    title: str
    description: str
    start_time: datetime.datetime | None
    end_time: datetime.datetime | None
    status: str
    max_participants: int
    current_participants: int = 0
    created_at: datetime.datetime
    creator_id: int


class HackathonCreateSchema(BaseModel):
    title: str
    description: str
    max_participants: int
    creator_id: int


class HackathonSchema(HackathonBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
