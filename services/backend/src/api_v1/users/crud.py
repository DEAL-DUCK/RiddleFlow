from fastapi import HTTPException
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.users.schemas import UserSchema
from services.backend.src.api_v1.users.schemas import UserCreateSchema
from services.backend.src.core.models import User
from services.backend.src.core.models.profile import Profile
async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def create_user(
        session: AsyncSession,
        user_in: UserCreateSchema
) -> User:

    existing_user = await session.scalar(
        select(User).where(User.username == user_in.username)
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Username "{user_in.username}" already exists'
        )


    existing_user = await session.scalar(
        select(User).where(User.email == user_in.email)
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Email "{user_in.email}" already exists'
        )

    user = User(**user_in.model_dump())
    session.add(user)
    await session.flush()

    profile = Profile(user_id=user.id)
    session.add(profile)

    await session.commit()
    await session.refresh(user)

    return user


async def delete_user(session: AsyncSession, user_id: int) -> dict:
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    profile = await session.scalar(select(Profile).where(Profile.user_id == user_id))
    if profile:
        await session.delete(profile)
        await session.commit()
    await session.delete(user)
    await session.commit()

    return {'ok': True}


