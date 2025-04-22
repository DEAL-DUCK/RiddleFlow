import enum
from typing import TYPE_CHECKING
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Enum, DateTime, Index, Integer
from sqlalchemy.sql import func
import datetime
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .user import User
    from .hackathon import Hackathon


class ParticipationStatus(enum.Enum):
    REGISTERED = "REGISTERED"
    COMPLETED = "COMPLETED"
    DISQUALIFIED = "DISQUALIFIED"
    REFUSED = "REFUSED"


class HackathonUserAssociation(Base, IdIntPkMixin):
    __tablename__ = "hackathon_user_association"
    __table_args__ = (
        UniqueConstraint("hackathon_id", "user_id", name="idx_unique_hackathon_user"),
        Index("idx_hackathon_user_user_id", "user_id"),
    )
    hackathon_id: Mapped[int] = mapped_column(
        ForeignKey("hackathons.id"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    user_status: Mapped[ParticipationStatus] = mapped_column(
        Enum(ParticipationStatus),
        default=ParticipationStatus.REGISTERED,
        server_default="REGISTERED",
    )
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    hackathon: Mapped["Hackathon"] = relationship(
        back_populates="users_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(
        back_populates="hackathons_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
