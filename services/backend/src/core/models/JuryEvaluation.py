from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, UniqueConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base

if TYPE_CHECKING:
    from .jury import Jury
    from .hackathon_submission import HackathonSubmission
    from .hackathon import Hackathon


class JuryEvaluation(Base):
    __tablename__ = 'jury_evaluations'
    __table_args__ = (

        UniqueConstraint('jury_id', 'submission_id', name='uq_jury_submission'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    jury_id: Mapped[int] = mapped_column(ForeignKey('jurys.id'))
    submission_id: Mapped[int] = mapped_column(ForeignKey('submissions.id'))
    score: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    jury: Mapped[Jury] = relationship(back_populates="evaluations")
    submission: Mapped[HackathonSubmission] = relationship(back_populates="evaluations")
    hackathon: Mapped[Hackathon] = relationship(back_populates="jury_evaluations")