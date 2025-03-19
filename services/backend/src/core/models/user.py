from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class User(Base):
    username: Mapped[str] = mapped_column(String(40), unique=True)
    # password, email/phone,
