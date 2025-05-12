from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer
from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .hackathon import Hackathon
    from .JuryEvaluation import JuryEvaluation

class Jury(Base):
    __tablename__ = 'jurys'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        unique=True,
        nullable=False
    )
    user: Mapped["User"] = relationship(
        back_populates="jury_profile",
        lazy="selectin"
    )


    judged_hackathons: Mapped[list["Hackathon"]] = relationship(
        secondary="jury_hackathon_association",
        back_populates="jury_members",
        lazy="selectin"
    )

    specialization: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    evaluations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evaluations: Mapped[list["JuryEvaluation"]] = relationship(
        back_populates="jury",
        cascade="all, delete-orphan",
        lazy="selectin"
    )