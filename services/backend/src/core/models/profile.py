from typing import TYPE_CHECKING
from .base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Date
from datetime import date
from .mixins.int_pk_id import IdIntPkMixin

if TYPE_CHECKING:
    from .user import User


class Profile(Base, IdIntPkMixin):
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(String(1000), nullable=True)
    country: Mapped[str] = mapped_column(String(30), nullable=True)
    city: Mapped[str] = mapped_column(String(30), nullable=True)
    job: Mapped[str] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(nullable=True, unique=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
    )

    user: Mapped["User"] = relationship(back_populates="profile")
