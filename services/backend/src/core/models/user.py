from typing import TYPE_CHECKING

# from .hackathon_user_association import HackathonUserAssociation
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Index, DateTime
from sqlalchemy_utils import EmailType
from sqlalchemy.sql import func
import datetime

if TYPE_CHECKING:
    from .profile import Profile
    from .hackathon import Hackathon
    from .submission import Submission


class User(Base):
    __table_args__ = (
        Index("idx_user_email", "email", unique=True),
        Index("idx_user_username", "username", unique=True),
    )
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(EmailType, unique=True, nullable=False)
    is_creator: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_participant: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
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
