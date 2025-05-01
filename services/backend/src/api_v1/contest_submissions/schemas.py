from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ContestSubmissionStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"
    DISQUALIFIED = "DISQUALIFIED"


class ContestSubmissionBase(BaseModel):
    code: str
    status: ContestSubmissionStatus = ContestSubmissionStatus.DRAFT


class ContestSubmissionCreate(BaseModel):
    task_id: int
    code: str


class ContestSubmissionRead(ContestSubmissionBase):
    id: int
    task_id: int
    user_id: int
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContestSubmissionUpdate(BaseModel):
    code_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ContestSubmissionStatus] = None


class SimpleJuryEvaluation(BaseModel):
    score: float
    comment: str
    jury_name: str
