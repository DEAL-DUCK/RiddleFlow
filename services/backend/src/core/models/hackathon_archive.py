from .base import Base
from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Enum, Integer, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .mixins.int_pk_id import IdIntPkMixin

class HackathonStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"

if TYPE_CHECKING:
    from .hackathon_group_association import HackathonGroupAssociation
    from .hackathon_user_association import HackathonUserAssociation
    from .user import User
    from .hackathon_task import HackathonTask
    from .hackathon import Hackathon




class ArchivedHackathon(Base):
    __tablename__ = 'archived_hackathons'

    id: Mapped[int] = mapped_column(ForeignKey('hackathons.id'), primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(900))
    original_status: Mapped[HackathonStatus] = mapped_column(Enum(HackathonStatus))
    max_participants: Mapped[int] = mapped_column(Integer)
    current_participants: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    allow_teams: Mapped[bool] = mapped_column(Boolean)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255))
    archived_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    archive_reason: Mapped[Optional[str]] = mapped_column(String(255))
    archived_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    archived_by: Mapped[Optional["User"]] = relationship(lazy="selectin")
    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id],
        lazy="selectin"
    )
    original: Mapped[Optional["Hackathon"]] = relationship(back_populates="archived_record")