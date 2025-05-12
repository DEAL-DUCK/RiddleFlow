import enum
from typing import TYPE_CHECKING

from .base import Base
from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTable,
    SQLAlchemyUserDatabase,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Index, DateTime, Enum
from sqlalchemy.sql import func
from datetime import datetime

from core.types.user_id import UserIdType
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .profile import Profile
    from .hackathon import Hackathon
    from .hackathon_submission import HackathonSubmission
    from .contest_submission import ContestSubmission
    from sqlalchemy.ext.asyncio import AsyncSession
    from .group_user_association import GroupUserAssociation
    from .hackathon_user_association import HackathonUserAssociation
    from .contest_user_association import ContestUserAssociation
    from .jury import Jury


class UserRole(enum.Enum):
    PARTICIPANT = "PARTICIPANT"
    CREATOR = "CREATOR"


class User(Base, IdIntPkMixin, SQLAlchemyBaseUserTable[UserIdType]):
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
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    created_hackathons: Mapped[list["Hackathon"]] = relationship(
        "Hackathon",
        back_populates="creator",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    created_contests: Mapped[list["Hackathon"]] = relationship(
        "Contest",
        back_populates="creator",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    hackathons_details: Mapped[list["HackathonUserAssociation"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    contests_details: Mapped[list["ContestUserAssociation"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    hackathon_submissions: Mapped[list["HackathonSubmission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    contest_submissions: Mapped[list["ContestSubmission"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    groups_details: Mapped[list["GroupUserAssociation"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    jury_profile: Mapped["Jury"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)
