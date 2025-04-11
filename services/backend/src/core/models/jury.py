# jury.py
from typing import TYPE_CHECKING
from . import User
from .JuryEvaluation import JuryEvaluation
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.sql import func
from datetime import datetime

if TYPE_CHECKING:
    from .hackathon import Hackathon
    from .submission import Submission

# Таблица для связи многие-ко-многим Jury и Hackathon
jury_hackathon_association = Table(
    'jury_hackathon_association',
    Base.metadata,
    Column('jury_id', ForeignKey('jurys.id'), primary_key=True),
    Column('hackathon_id', ForeignKey('hackathons.id'), primary_key=True)
)


class Jury(Base):
    """
    Модель жюри, наследуется от User с дополнительными связями
    """
    __tablename__ = 'jurys'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    user: Mapped["User"] = relationship(back_populates="jury_profile")

    # Связи
    judged_hackathons: Mapped[list["Hackathon"]] = relationship(
        secondary=jury_hackathon_association,
        back_populates="jury_members"
    )

    # Дополнительные поля
    specialization: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Связь с оценками (через ассоциативную таблицу)
    evaluations: Mapped[list["JuryEvaluation"]] = relationship(
        back_populates="jury",
        cascade="all, delete-orphan"
    )