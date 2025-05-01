from pydantic import BaseModel, ConfigDict, field_validator, model_validator, Field
import datetime

# import enum
#
# class ContestStatus(enum.Enum):
#     PLANNED = "planned"
#     ACTIVE = "active"
#     COMPLETED = "completed"
#     CANCELED = "canceled"


class ContestBaseSchema(BaseModel):
    title: str
    description: str
    start_time: datetime.datetime | None
    end_time: datetime.datetime | None
    status: str
    max_participants: int
    current_participants: int = 0
    created_at: datetime.datetime
    updated_at: datetime.datetime
    allow_teams: bool
    logo_url: str
    creator_id: int


class ContestCreateSchema(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=900)
    allow_teams: bool
    max_participants: int = Field(..., gt=0)
    # logo_url: str | None = None
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
        return values

    @model_validator(mode="before")
    def check_max_participants(cls, values):
        max_participants = values.get("max_participants")
        if max_participants is not None and max_participants <= 0:
            raise ValueError("max_participants must be greater than zero")
        return values

    @model_validator(mode="before")
    def check_tittle(cls, values):
        title = values.get("title")
        if len(title) > 100:
            raise ValueError("The length is more than 100")

        return values

    # включить на проде
    # if (
    #     start_time
    #     and start_time[:10]
    #     == datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    # ):
    #     raise ValueError("start_time cannot be today")


class ContestUpdatePartial(ContestCreateSchema):
    title: str | None = None
    description: str | None = None
    max_participants: int | None = None
    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    allow_teams: bool | None = None
    # logo_url: str | None = None


class ContestSchema(ContestBaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id: int
