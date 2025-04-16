from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.profiles.schemas import ProfileUpdateSchema, ProfileSchema
from core.models import Profile


async def get_profile(session: AsyncSession, user_id: int) -> Profile | None:
    result = await session.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def update_profile(
    session: AsyncSession,
    profile: ProfileSchema,
    profile_update: ProfileUpdateSchema,
) -> ProfileSchema:
    for name, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(profile, name, value)
    await session.commit()
    return profile
