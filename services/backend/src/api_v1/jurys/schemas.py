from pydantic import BaseModel


class JuryResponse(BaseModel):
    status: str
    jury_id: int
    hackathon_id: int
    user_id: int

    class Config:
        from_attributes = True
class JuryCreate(BaseModel):
    user_id: int
    hackathon_id: int