from .base import Base
from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, Enum, Integer, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .contest import ContestStatus
from .mixins.int_pk_id import IdIntPkMixin


if TYPE_CHECKING:
    from .contest_group_association import ContestGroupAssociation
    from .contest_user_association import ContestUserAssociation
    from .user import User
    from .contest_task import ContestTask
    from .contest import Contest

class ArchivedContest(Base):
    __tablename__ = 'archived_contests'

    id: Mapped[int] = mapped_column(primary_key=True)
    original_contest_id: Mapped[int] = mapped_column(
        ForeignKey('contests.id', ondelete="CASCADE"),
        unique=True
    )
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(900))
    original_status: Mapped[ContestStatus] = mapped_column(Enum(ContestStatus))
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

    original: Mapped["Contest"] = relationship(back_populates="archived_record")
    archived_by: Mapped[Optional["User"]] = relationship(lazy="selectin")
    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id],
        lazy="selectin"
    )