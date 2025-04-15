import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.sql import func

from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Index, DateTime, Enum
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .hackathon import Hackathon
    from .groups import Group


class TeamStatus(enum.Enum):
    REGISTERED = "REGISTERED"
    COMPLETED = "COMPLETED"
    DISQUALIFIED = "DISQUALIFIED"


class HackathonGroupAssociation(Base, IdIntPkMixin):
    __tablename__ = "hackathon_group_association"
    __table_args__ = (
        UniqueConstraint("hackathon_id", "group_id", name="idx_unique_hackathon_group"),
        Index("idx_hackathon_group_group_id", "group_id"),
    )
    hackathon_id: Mapped[int] = mapped_column(
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"),
        nullable=False,
    )

    group_status: Mapped[TeamStatus] = mapped_column(
        Enum(TeamStatus),
        default=TeamStatus.REGISTERED,
        server_default="REGISTERED",
    )
    registration_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    hackathon: Mapped["Hackathon"] = relationship(
        back_populates="groups_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
    group: Mapped["Group"] = relationship(
        back_populates="hackathons_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
