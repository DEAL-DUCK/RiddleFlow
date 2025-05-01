from datetime import datetime
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey, Text, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from typing import TYPE_CHECKING
from .mixins.int_pk_id import IdIntPkMixin


class TestCase(Base, IdIntPkMixin):
    __tablename__ = "test_cases"
    task_id: Mapped[int] = mapped_column(
        ForeignKey("contest_tasks.id"),
        nullable=False,
    )
    input: Mapped[str] = mapped_column(String, nullable=False)
    expected_output: Mapped[str] = mapped_column(String, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False)
