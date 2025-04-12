from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, Index, DateTime
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
import enum
import datetime
from .base import Base

if TYPE_CHECKING:
    from .profile import Profile
    from .hackathon import Hackathon
    from .submission import Submission
    from .jury import Jury
    from .hackathon_user_association import HackathonUserAssociation


class UserRole(enum.Enum):
    PARTICIPANT = "PARTICIPANT"
    CREATOR = "CREATOR"
    JURY = "JURY"


class User(Base):
    __table_args__ = (
        Index("idx_user_email", "email", unique=True),
        Index("idx_user_username", "username", unique=True),
    )

    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(EmailType, unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        name="user_role",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        uselist=False,
        lazy="selectin"
    )

    created_hackathons: Mapped[list["Hackathon"]] = relationship(
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
        lazy="selectin"
    )

    jury_profile: Mapped["Jury"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )