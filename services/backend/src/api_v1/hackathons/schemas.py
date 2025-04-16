from pydantic import BaseModel, ConfigDict, field_validator, model_validator
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
    start_time: datetime.datetime | None
    end_time: datetime.datetime | None = None

    @model_validator(mode="before")
    def check_times(cls, values):
        start_time = values.get("start_time")
        end_time = values.get("end_time")
        if start_time and end_time and end_time < start_time:
            raise ValueError("end_time must be after start_time")
        if start_time and start_time[-1] != "Z":
            raise ValueError("start_time must be in UTC")
        if end_time and end_time[-1] != "Z":
            raise ValueError("end_time must be in UTC")
        if end_time and not start_time:
            raise ValueError("start_time must be provided if end_time is given")

        # включить на проде
        # if (
        #     start_time
        #     and start_time[:10]
        #     == datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        # ):
        #     raise ValueError("start_time cannot be today")
        return values


class HackathonUpdatePartial(HackathonCreateSchema):
    title: str | None = None
    description: str | None = None
    max_participants: int | None = None
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    status: str = None


class HackathonSchema(HackathonBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
