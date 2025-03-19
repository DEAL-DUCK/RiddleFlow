from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class Profile(Base):
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    # email: Mapped[str] = mapped_column()  # добавить pydantic[email]
    # bio: Mapped[str] = mapped_column()
    # photo: Mapped[str] = mapped_column()
    # birthday_data: Mapped[str] = mapped_column()
    # country: Mapped[str] = mapped_column()
    # city: Mapped[str] = mapped_column()
    # job: Mapped[str] = mapped_column()
    # phone_number: Mapped[str] = mapped_column()
