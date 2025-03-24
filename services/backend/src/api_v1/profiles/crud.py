#from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.profiles.schemas import ProfileUpdateSchema, ProfileSchema
from services.backend.src.core.models import Profile



async def get_profile(session: AsyncSession, user_id: int) -> Profile | None:
    return await session.get(Profile, user_id)


async def update_profile(session: AsyncSession, profile: ProfileSchema, profile_update: ProfileUpdateSchema):
    for name, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(profile, name, value)
    await session.commit()
    return profile
