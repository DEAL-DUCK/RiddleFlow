from .base import Base
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Enum, Integer, ForeignKey, Index
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .mixins.int_pk_id import IdIntPkMixin


if TYPE_CHECKING:
    from .hackathon_user_association import HackathonUserAssociation
    from .user import User
    from .task import Task


class HackathonStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class Hackathon(Base, IdIntPkMixin):
    __table_args__ = (
        Index("idx_hackathon_status", "hackathon_status"),
        # Index("idx_hackathon_creator_id", "creator_id"),
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(900), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[HackathonStatus] = mapped_column(
        Enum(HackathonStatus),
        name="hackathon_status",
        default=HackathonStatus.PLANNED,
        server_default="PLANNED",
    )
    max_participants: Mapped[int] = mapped_column(Integer, nullable=False)
    current_participants: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    creator: Mapped["User"] = relationship(
        back_populates="created_hackathons",
        lazy="selectin",
    )
    users_details: Mapped[list["HackathonUserAssociation"]] = relationship(
        back_populates="hackathon",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="hackathon",
        cascade="all, delete-orphan",
    )
