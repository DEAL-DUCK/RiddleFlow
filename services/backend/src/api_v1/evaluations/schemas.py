from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator, model_validator


class EvaluationUpdateSchema(BaseModel):
    comment: Optional[str] = Field(None, max_length=500)
    score: Optional[float] = Field(None, ge=0, le=10)

class EvaluationCreateSchema(BaseModel):
    score: int = Field(..., gt=0, le=10)
    comment: str | None = Field(None, max_length=500)



class EvaluationReadSchema(EvaluationCreateSchema):
    id: int
    jury_id: int
    submission_id: int
    created_at: datetime

    class Config:
        from_attributes = True