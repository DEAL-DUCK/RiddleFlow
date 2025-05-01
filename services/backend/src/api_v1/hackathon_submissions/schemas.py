from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class HackathonSubmissionStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"
    DISQUALIFIED = "DISQUALIFIED"


class HackathonSubmissionBase(BaseModel):
    code_url: str
    description: str
    status: HackathonSubmissionStatus = HackathonSubmissionStatus.DRAFT


class HackathonSubmissionCreate(HackathonSubmissionBase):
    task_id: int


class HackathonSubmissionRead(HackathonSubmissionBase):
    id: int
    task_id: int
    user_id: int
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HackathonSubmissionUpdate(BaseModel):
    code_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[HackathonSubmissionStatus] = None


class SimpleJuryEvaluation(BaseModel):
    score: float
    comment: str
    jury_name: str
