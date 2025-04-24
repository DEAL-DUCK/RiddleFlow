from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import User
if TYPE_CHECKING:
    from core.models import User,Hackathon


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


# ненадобность, из-за подключённой регистрации

# async def create_user(session: AsyncSession, user_in: UserCreateSchema) -> User:
#     user = User(**user_in.model_dump())
#     session.add(user)
#     await session.commit()
#     profile = Profile(user_id=user.id)
#     session.add(profile)
#     await session.commit()
#     return user

# ПОТОМ УДАЛЮ ЭТО ДЛЯ УДОБСТВА И СОЗДАНИЯ АДМИНА
async def for_ivan_func(session: AsyncSession, user_id: int):
    user = await session.get(User, user_id)
    user.is_superuser = True
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
