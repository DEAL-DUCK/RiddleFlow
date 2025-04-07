from datetime import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING
from .mixins.int_pk_id import IdIntPkMixin


if TYPE_CHECKING:
    from .task import Task
    from .user import User


class SubmissionStatus(str, Enum):
    DRAFT = "DRAFT"  # Черновик
    SUBMITTED = "SUBMITTED"  # Отправлено
    GRADED = "GRADED"  # Проверено
    DISQUALIFIED = "DISQUALIFIED"  # Отклонено


class Submission(Base, IdIntPkMixin):
    code_url: Mapped[str] = mapped_column(String(255))  # Ссылка на репозиторий
    # commit_hash: Mapped[str] = mapped_column(String(40))  # Контроль версий
    description: Mapped[str] = mapped_column(Text)  # Описание решения

    # # Медиа
    # demo_url: Mapped[str] = mapped_column(String(255), nullable=True)  # Демо
    # video_url: Mapped[str] = mapped_column(String(255), nullable=True)  # Видео

    # Статус и оценки
    status: Mapped[SubmissionStatus] = mapped_column(default=SubmissionStatus.DRAFT)
    # score: Mapped[float] = mapped_column(nullable=True)  # Итоговый балл
    # feedback: Mapped[str] = mapped_column(Text, nullable=True)  # Комментарии жюри

    # Временные метки
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    graded_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=True)

    task: Mapped["Task"] = relationship(back_populates="submissions")
    user: Mapped["User"] = relationship(back_populates="submissions")
    # attachments: Mapped[list["SubmissionAttachment"]] = relationship(
    #     cascade="all, delete-orphan"
    # )
