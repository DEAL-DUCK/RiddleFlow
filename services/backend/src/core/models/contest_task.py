import enum
from datetime import datetime
from sqlalchemy import (
    JSON,
    Text,
    ForeignKey,
    String,
    Float,
    DateTime,
    Index,
    Integer,
    Enum, Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base
from typing import TYPE_CHECKING
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .contest import Contest
    from .contest_submission import ContestSubmission


class ContestTask(Base, IdIntPkMixin):
    __tablename__ = "contest_tasks"
    __table_args__ = (Index("idx_task_contest", "contest_id"),)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    contest_id: Mapped[int] = mapped_column(
        ForeignKey("contests.id"),
        nullable=False,
    )
    max_attempts: Mapped[int] = mapped_column(default=5, nullable=False)  # Максимальное количество попыток
    current_attempts: Mapped[int] = mapped_column(default=0, nullable=False)  # Текущее количество решений
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    memory_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    # creator: Mapped["User"] = relationship(back_populates="created_tasks")
    contest: Mapped["Contest"] = relationship(back_populates="tasks")
    submissions: Mapped[list["ContestSubmission"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    is_archived : Mapped[bool] = mapped_column(Boolean,default=False)

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
