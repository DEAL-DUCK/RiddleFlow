from fastapi import Depends

from core.authentication.user_manager import UserManager
from .users import get_users_db


async def get_user_manager(user_db=Depends(get_users_db)):
    yield UserManager(user_db)
