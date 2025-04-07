from typing import TYPE_CHECKING

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from core.models import db_helper, User


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(session: "AsyncSession" = Depends(db_helper.session_getter)):
    yield User.get_db(session=session)
