from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user
from api_v1.profiles.schemas import ProfileUpdateSchema, ProfileSchema
from core.models import Profile, db_helper


async def get_profile(session: AsyncSession, user_id: int) -> Profile | None:
    result = await session.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def get_profile_by_username(
        username: str,
        session: AsyncSession = Depends(db_helper.session_getter),
        user = Depends(current_active_user)
) -> ProfileSchema:
    result = await session.execute(
        select(Profile)
        .where(Profile.first_name == username)
    )
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with username '{username}' not found")


    return ProfileSchema.model_validate(profile)


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
