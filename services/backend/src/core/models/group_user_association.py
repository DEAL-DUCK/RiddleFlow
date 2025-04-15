import enum
from typing import TYPE_CHECKING
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Enum, DateTime, Index
from sqlalchemy.sql import func
import datetime
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .user import User
    from .group import Group


class ParticipationStatus(enum.Enum):
    REGISTERED = "REGISTERED"
    COMPLETED = "COMPLETED"
    DISQUALIFIED = "DISQUALIFIED"


class GroupUserAssociation(Base, IdIntPkMixin):
    __tablename__ = "group_user_association"
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="idx_unique_group_user"),
        Index("idx_group_user_user_id", "user_id"),
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="groups_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
    group: Mapped["Group"] = relationship(
        back_populates="users_details",
        cascade="save-update, merge",
        lazy="selectin",
    )
