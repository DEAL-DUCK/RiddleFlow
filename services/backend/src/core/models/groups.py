import enum
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, Integer, ForeignKey

from .mixins.int_pk_id import IdIntPkMixin
from .base import Base


class GroupType(enum.Enum):
    TEAM = "TEAM"
    JURY = "JURY"


if TYPE_CHECKING:
    from .hackathon import Hackathon
    from .hackathon_group_association import HackathonGroupAssociation
    from .group_user_association import GroupUserAssociation


class Group(Base, IdIntPkMixin):
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(
        Enum(GroupType),
        default=GroupType.TEAM,
        server_default="TEAM",
    )
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
        default=0,
        server_default="0",
    )

    users_details: Mapped[list["GroupUserAssociation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    hackathons_details: Mapped[list["HackathonGroupAssociation"]] = relationship(
        back_populates="hackathon",
        cascade="all, delete-orphan",
    )
