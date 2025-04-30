from .base import Base
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Enum, Integer, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .mixins.int_pk_id import IdIntPkMixin


if TYPE_CHECKING:
    from .contest_group_association import ContestGroupAssociation
    from .contest_user_association import ContestUserAssociation
    from .user import User
    from .task import Task


class ContestStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class Contest(Base, IdIntPkMixin):
    __table_args__ = (Index("idx_contests_status", "contest_status"),)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(900), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ContestStatus] = mapped_column(
        Enum(ContestStatus),
        name="contest_status",
        default=ContestStatus.PLANNED,
        server_default="PLANNED",
    )
    max_participants: Mapped[int] = mapped_column(Integer, nullable=False)
    current_participants: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    allow_teams: Mapped[bool] = mapped_column(Boolean, default=False)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    creator: Mapped["User"] = relationship(
        back_populates="created_contests",
        lazy="selectin",
    )
    users_details: Mapped[list["ContestUserAssociation"]] = relationship(
        back_populates="contest",
        cascade="all, delete-orphan",
    )
    # tasks: Mapped[list["Task"]] = relationship(
    #     back_populates="contest",
    #     cascade="all, delete-orphan",
    # )
    groups_details: Mapped[list["ContestGroupAssociation"]] = relationship(
        back_populates="contest",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
