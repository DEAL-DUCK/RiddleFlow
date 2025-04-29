from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import User, GroupUserAssociation

if TYPE_CHECKING:
    from core.models import User,Hackathon


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user(session: AsyncSession, user_id: int = None) -> User | None:
    return await session.get(User, user_id)
async def del_user(session:AsyncSession,user_id:int):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return f'user with id : {user_id} not found'

    await session.delete(user)
    await session.commit()
    return f'user with id : {user_id} deleted'

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
