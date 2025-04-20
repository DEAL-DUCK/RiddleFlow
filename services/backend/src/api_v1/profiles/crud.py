from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from api_v1.auth.fastapi_users import current_active_user
from api_v1.profiles.schemas import ProfileUpdateSchema, ProfileSchema
from core.models import Profile, db_helper, User


async def get_profile(session: AsyncSession, user_id: int) -> Profile | None:
    result = await session.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def get_profile_by_username(
        username: str,
        session: AsyncSession = Depends(db_helper.session_getter),
        current_user: User = Depends(current_active_user)
) -> ProfileSchema:
    result = await session.execute(
        select(User)
        .where(User.username == username)
        .options(selectinload(User.profile))
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found"
        )
    if not user.profile:
        user.profile = Profile(
            user_id=user.id,
            first_name=None,
            last_name=None,
            birth_date=None
        )
        session.add(user.profile)
        await session.commit()
        await session.refresh(user)

    profile_data = user.profile.__dict__
    profile_data.pop("_sa_instance_state", None)
    profile_data["username"] = user.username

    return ProfileSchema(**profile_data)


async def update_profile(
        session: AsyncSession,
        profile: Profile,
        profile_update: ProfileUpdateSchema,
) -> ProfileSchema:
    update_data = profile_update.model_dump(exclude_unset=True)

    for field, new_value in update_data.items():
        if new_value == "string":
            continue

        setattr(profile, field, new_value)

    await session.commit()
    await session.refresh(profile)
    return ProfileSchema.model_validate(profile)
