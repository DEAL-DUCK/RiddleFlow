import enum
from typing import TYPE_CHECKING
from .hackathon_user_association import HackathonUserAssociation
from .base import Base
from fastapi_users.db import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Index, DateTime, Enum
from sqlalchemy.sql import func
import datetime

if TYPE_CHECKING:
    from .profile import Profile
    from .hackathon import Hackathon
    from .submission import Submission
    from sqlalchemy.ext.asyncio import AsyncSession


class UserRole(enum.Enum):
    PARTICIPANT = "PARTICIPANT"
    CREATOR = "CREATOR"


class User(Base, SQLAlchemyBaseUserTable[int]):
    __table_args__ = (
        # Index("idx_user_email", "email", unique=True),
        Index("idx_user_username", "username", unique=True),
    )
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    user_role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    profile: Mapped["Profile"] = relationship(
        "Profile", back_populates="user", uselist=False
    )

    created_hackathons: Mapped[list["Hackathon"]] = relationship(
        "Hackathon",
        back_populates="creator",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    hackathons_details: Mapped[list["HackathonUserAssociation"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @classmethod
    def get_db(cls, session: AsyncSession):
        return SQLAlchemyUserDatabase(session, User)
