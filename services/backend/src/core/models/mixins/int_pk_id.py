from sqlalchemy.orm import Mapped, mapped_column

from core.types.user_id import UserIdType


class IdIntPkMixin:
    id: Mapped[UserIdType] = mapped_column(primary_key=True)
