from datetime import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING
from .mixins.int_pk_id import IdIntPkMixin


if TYPE_CHECKING:
    from .user import User
    from .contest_task import ContestTask


class SubmissionStatus2(str, Enum):
    DRAFT = "DRAFT"  # Черновик
    SUBMITTED = "SUBMITTED"  # Отправлено
    GRADED = "GRADED"  # Проверено
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"


class ContestSubmission(Base, IdIntPkMixin):
    __tablename__ = "contest_submissions"
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubmissionStatus2] = mapped_column(default=SubmissionStatus2.DRAFT)
    # score: Mapped[float] = mapped_column(nullable=True)  # Итоговый балл
    # feedback: Mapped[str] = mapped_column(Text, nullable=True)  # Комментарии жюри
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    graded_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    task_id: Mapped[int] = mapped_column(ForeignKey("contest_tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task: Mapped["ContestTask"] = relationship(back_populates="submissions")
    user: Mapped["User"] = relationship(back_populates="contest_submissions")
