from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class SubmissionStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"
    DISQUALIFIED = "DISQUALIFIED"

class SubmissionBase(BaseModel):
    code_url: str
    description: str
    status: SubmissionStatus = SubmissionStatus.DRAFT

class SubmissionCreate(SubmissionBase):
    task_id: int
    user_id: int

class SubmissionRead(SubmissionBase):
    id: int
    task_id: int
    user_id: int
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SubmissionUpdate(BaseModel):
    code_url: Optional[str] = None
    description: Optional[str] = None
    status: Optional[SubmissionStatus] = None
class SimpleJuryEvaluation(BaseModel):
    score: float
    comment: str
    jury_name: str