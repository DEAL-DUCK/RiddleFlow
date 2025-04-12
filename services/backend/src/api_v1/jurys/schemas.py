from typing import List

from services.backend.src.core.models import User
from pydantic import BaseModel

class Jury(User):
    user_id : int
    hackathons_active : List
    evaluate : int
