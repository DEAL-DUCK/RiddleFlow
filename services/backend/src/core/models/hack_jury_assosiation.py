from datetime import datetime

from sqlalchemy import ForeignKey, func, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class JuryHackathonAssociation(Base):
    __tablename__ = "jury_hackathon_association"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jury_id: Mapped[int] = mapped_column(ForeignKey("jurys.id"))
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    __table_args__ = (
        Index('idx_jury_hackathon_unique', 'jury_id', 'hackathon_id', unique=True),
    )