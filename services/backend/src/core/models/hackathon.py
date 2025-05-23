from .base import Base
from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Enum, Integer, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .mixins.int_pk_id import IdIntPkMixin


if TYPE_CHECKING:
    from .hackathon_group_association import HackathonGroupAssociation
    from .hackathon_user_association import HackathonUserAssociation
    from .user import User
    from .hackathon_task import HackathonTask
    from .jury import Jury
    from .JuryEvaluation import JuryEvaluation



class HackathonStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class Hackathon(Base, IdIntPkMixin):
    __table_args__ = (Index("idx_hackathon_status", "hackathon_status"),)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(900), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[HackathonStatus] = mapped_column(
        Enum(HackathonStatus),
        name="hackathon_status",
        default=HackathonStatus.PLANNED,
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
    is_archived : Mapped[bool] = mapped_column(Boolean,default=False)
    creator: Mapped["User"] = relationship(
        back_populates="created_hackathons",
        lazy="selectin",
    )
    users_details: Mapped[list["HackathonUserAssociation"]] = relationship(
        back_populates="hackathon",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[list["HackathonTask"]] = relationship(
        back_populates="hackathon",
        cascade="all, delete-orphan",
    )
    groups_details: Mapped[list["HackathonGroupAssociation"]] = relationship(
        back_populates="hackathon",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    jury_members: Mapped[list["Jury"]] = relationship(
        secondary="jury_hackathon_association",
        back_populates="judged_hackathons",
        lazy="selectin"
    )
    jury_evaluations: Mapped[list["JuryEvaluation"]] = relationship(
        back_populates="hackathon",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
