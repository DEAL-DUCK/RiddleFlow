import asyncio
import contextlib

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from core.authentication.user_manager import UserManager
from core.models import db_helper, User, Profile
from api_v1.dependencies.authentication.users import get_users_db
from api_v1.users.schemas import UserCreate
from api_v1.dependencies.authentication.user_manager import get_user_manager

# from fastapi_users.exceptions import UserAlreadyExists

# get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_users_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

default_email = "admin3@yandex.ru"
default_password = "111"
default_is_active = True
default_is_superuser = True
default_is_verified = True
default_username = "admin3"
default_user_role = "CREATOR"


async def create_user(
    user_manager: UserManager,
    user_create: UserCreate,
) -> User:
    user = await user_manager.create(
        user_create=user_create,
        safe=False,
    )
    return user


async def create_superuser(
    email: str = default_email,
    password: str = default_password,
    is_active: str = default_is_active,
    is_superuser: str = default_is_superuser,
    is_verified: str = default_is_verified,
    username: str = default_username,
    user_role: str = default_user_role,
):
    user_create = UserCreate(
        email=email,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
        username=username,
        user_role=user_role,
    )
    async with db_helper.session_factory() as session:
        async with get_users_db_context(session) as users_db:
            async with get_user_manager_context(users_db) as user_manager:
                user = await create_user(
                    user_manager,
                    user_create,
                )
                profile = Profile(user_id=user.id)
                session.add(profile)
                await session.commit()
                return user


if __name__ == "__main__":
    asyncio.run(create_superuser())
