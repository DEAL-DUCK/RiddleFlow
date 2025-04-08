import enum
from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy import (
    JSON,
    Text,
    ForeignKey,
    String,
    Float,
    DateTime,
    Index,
    Integer,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hackathon import Hackathon
    from .user import User
    from .submission import Submission

class TaskType(enum.Enum):
    CODING = "CODING"  # Программирование
    QUIZ = "QUIZ"  # Тестовые вопросы
    DESIGN = "DESIGN"  # Дизайн/UI/UX
    DATA_SCIENCE = "DATA_SCIENCE"  # Анализ данных
    HARDWARE = "HARDWARE"  # IoT/железо


class Task(Base):
    __table_args__ = (
        Index("idx_task_hackathon", "hackathon_id"),
        Index("idx_task_type", "task_type", "hackathon_id"),
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[TaskType] = mapped_column(Enum(TaskType), nullable=False)
    hackathon_id: Mapped[int] = mapped_column(
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    hackathon: Mapped["Hackathon"] = relationship(back_populates="tasks")
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )




    # max_score: Mapped[int] = mapped_column(Integer, default=100)
    # deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    # is_required: Mapped[bool] = mapped_column(default=True)  # Обязательное/опциональное

    # Для автоматической проверки
    # evaluation_script: Mapped[str] = mapped_column(
    #     Text, nullable=True
    # )  # Путь к скрипту проверки
    # test_cases: Mapped[dict] = mapped_column(
    #     JSON, nullable=True
    # )  # {input: str, output: str, score: float}
    # time_limit: Mapped[int] = mapped_column(Integer, default=300)  # В секундах
    # memory_limit: Mapped[int] = mapped_column(Integer, default=512)  # В MB

    # Для разных типов заданий
    # starter_code: Mapped[str] = mapped_column(Text, nullable=True)  # Для CODING
    # questions: Mapped[list] = mapped_column(
    #     JSON, nullable=True
    # )  # Для QUIZ: [{question: str, options: [], correct: str}]
    # figma_template: Mapped[str] = mapped_column(
    #     String(255), nullable=True
    # )  # Для DESIGN
    # dataset_url: Mapped[str] = mapped_column(
    #     String(255), nullable=True
    # )  # Для DATA_SCIENCE

    # creator_id: Mapped[int] = mapped_column(
    #     ForeignKey("users.id"),
    #     nullable=False,
    # )

    # creator: Mapped["User"] = relationship(back_populates="created_tasks")
    # submissions: Mapped[list["Submission"]] = relationship(
    #     back_populates="task", cascade="all, delete-orphan"
    # )
