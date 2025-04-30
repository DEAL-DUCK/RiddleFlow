import enum
from datetime import datetime
from typing import TYPE_CHECKING


from sqlalchemy.sql import func

from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Index, DateTime, Enum
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .contest import Contest
    from .group import Group


class TeamStatus(enum.Enum):
    REGISTERED = "REGISTERED"
    COMPLETED = "COMPLETED"
    DISQUALIFIED = "DISQUALIFIED"
    REFUSED = "REFUSED"


class ContestGroupAssociation(Base, IdIntPkMixin):
    __tablename__ = "contest_group_association"
    __table_args__ = (
        UniqueConstraint("contest_id", "group_id", name="idx_unique_contest_group"),
        Index("idx_contest_group_group_id", "group_id"),
    )
    contest_id: Mapped[int] = mapped_column(
        ForeignKey("contests.id"),
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

    contest: Mapped["Contest"] = relationship(
        back_populates="groups_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
    group: Mapped["Group"] = relationship(
        back_populates="contests_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
