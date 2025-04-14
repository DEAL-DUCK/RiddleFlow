from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.users.schemas import UserCreateSchema
from core.models import User, Profile


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def create_user(session: AsyncSession, user_in: UserCreateSchema) -> User:
    user = User(**user_in.model_dump())
    session.add(user)
    await session.commit()
    profile = Profile(user_id=user.id)
    session.add(profile)
    await session.commit()
    return user
