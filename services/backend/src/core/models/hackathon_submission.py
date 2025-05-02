from datetime import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING
from .mixins.int_pk_id import IdIntPkMixin


if TYPE_CHECKING:
    from .hackathon_task import HackathonTask
    from .user import User
    from .JuryEvaluation import JuryEvaluation


class SubmissionStatus(str, Enum):
    DRAFT = "DRAFT"  # Черновик
    SUBMITTED = "SUBMITTED"  # Отправлено
    GRADED = "GRADED"  # Проверено
    DISQUALIFIED = "DISQUALIFIED"  # Отклонено


class HackathonSubmission(Base, IdIntPkMixin):
    __tablename__ = "hackathon_submissions"
    code_url: Mapped[str] = mapped_column(String(255))  # Ссылка на репозиторий
    description: Mapped[str] = mapped_column(Text)  # Описание решения
    status: Mapped[SubmissionStatus] = mapped_column(default=SubmissionStatus.DRAFT)
    # score: Mapped[float] = mapped_column(nullable=True)  # Итоговый балл
    # feedback: Mapped[str] = mapped_column(Text, nullable=True)  # Комментарии жюри
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    graded_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )

    task_id: Mapped[int] = mapped_column(ForeignKey("hackathon_tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task: Mapped["HackathonTask"] = relationship(back_populates="submissions")
    user: Mapped["User"] = relationship(back_populates="hackathon_submissions")
    evaluations: Mapped[list["JuryEvaluation"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
