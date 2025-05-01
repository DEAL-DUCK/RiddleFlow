import enum

from typing import TYPE_CHECKING
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Enum, DateTime, Index, Integer
from sqlalchemy.sql import func
from datetime import datetime
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .user import User
    from .contest import Contest


class ParticipationStatus2(enum.Enum):
    REGISTERED = "REGISTERED"
    COMPLETED = "COMPLETED"
    DISQUALIFIED = "DISQUALIFIED"
    REFUSED = "REFUSED"


class ContestUserAssociation(Base, IdIntPkMixin):
    __tablename__ = "contest_user_association"
    __table_args__ = (
        UniqueConstraint("contest_id", "user_id", name="idx_unique_contest_user"),
        Index("idx_contest_user_user_id", "user_id"),
    )
    contest_id: Mapped[int] = mapped_column(
        ForeignKey("contests.id"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    user_status: Mapped[ParticipationStatus2] = mapped_column(
        Enum(ParticipationStatus2),
        default=ParticipationStatus2.REGISTERED,
        server_default="REGISTERED",
    )
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    contest: Mapped["Contest"] = relationship(
        back_populates="users_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(
        back_populates="contests_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
