from datetime import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .user import User


class SubmissionStatus(str, Enum):
    DRAFT = "DRAFT"  # Черновик
    SUBMITTED = "SUBMITTED"  # Отправлено
    GRADED = "GRADED"  # Проверено
    DISQUALIFIED = "DISQUALIFIED"  # Отклонено


# submission.py
from datetime import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Text, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .user import User
    from .jury import JuryEvaluation


class SubmissionStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"
    DISQUALIFIED = "DISQUALIFIED"


class Submission(Base):
    __tablename__ = 'submissions'

    code_url: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[SubmissionStatus] = mapped_column(default=SubmissionStatus.DRAFT)

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=True
    )
    graded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True
    )

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    task: Mapped["Task"] = relationship(back_populates="submissions")
    user: Mapped["User"] = relationship(back_populates="submissions")

    evaluations: Mapped[list["JuryEvaluation"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan"
    )

    # commit_hash: Mapped[str] = mapped_column(String(40))  # Контроль версий


    # # Медиа
    # demo_url: Mapped[str] = mapped_column(String(255), nullable=True)  # Демо
    # video_url: Mapped[str] = mapped_column(String(255), nullable=True)  # Видео

    # Статус и оценки

    # score: Mapped[float] = mapped_column(nullable=True)  # Итоговый балл
    # feedback: Mapped[str] = mapped_column(Text, nullable=True)  # Комментарии жюри

    # Временные метки


    # team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=True)


    # attachments: Mapped[list["SubmissionAttachment"]] = relationship(
    #     cascade="all, delete-orphan"
    # )
