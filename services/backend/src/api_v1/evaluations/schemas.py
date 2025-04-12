from pydantic import BaseModel


class EvaluationSchema(BaseModel):
    submission_id: int
    jury_id : int
    comment : str
    score : float
