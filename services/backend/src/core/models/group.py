from datetime import datetime
import enum
from sqlalchemy.sql import func
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, Integer, ForeignKey, DateTime, Text

from .mixins.int_pk_id import IdIntPkMixin
from .base import Base


class GroupType(enum.Enum):
    TEAM = "TEAM"
    JURY = "JURY"


class GroupStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BANNED = "BANNED"


if TYPE_CHECKING:
    from .hackathon_group_association import HackathonGroupAssociation
    from .group_user_association import GroupUserAssociation


class Group(Base, IdIntPkMixin):
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[GroupType] = mapped_column(
        Enum(GroupType),
        default=GroupType.TEAM,
        server_default="TEAM",
    )
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    max_members: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    current_members: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    status: Mapped[GroupStatus] = mapped_column(
        Enum(GroupStatus),
        default=GroupStatus.ACTIVE,
        server_default="ACTIVE",
    )
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    social_media_links: Mapped[str] = mapped_column(Text, nullable=True)

    users_details: Mapped[list["GroupUserAssociation"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
    hackathons_details: Mapped[list["HackathonGroupAssociation"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )
