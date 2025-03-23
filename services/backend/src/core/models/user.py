from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum
from sqlalchemy_utils import EmailType
import enum

class UserRole(enum.Enum):
    PARTICIPANT = "participant"
    CREATOR = "creator"

class User(Base):
    username: Mapped[str] = mapped_column(String(40), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(EmailType, unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))
