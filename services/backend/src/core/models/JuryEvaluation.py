from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base

if TYPE_CHECKING:
    from .jury import Jury
    from .submission import Submission

class JuryEvaluation(Base):
    __tablename__ = 'jury_evaluations'

    jury_id: Mapped[int] = mapped_column(ForeignKey('jurys.id'), primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey('submissions.id'), primary_key=True)
    score: Mapped[float] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    jury: Mapped["Jury"] = relationship(back_populates="evaluations")
    submission: Mapped["Submission"] = relationship(back_populates="evaluations")