from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.profiles.crud import get_profile
from core.models import db_helper, Profile


async def get_profile_by_id(
    user_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Profile:
    profile = await get_profile(session=session, user_id=user_id)
    if profile is not None:
        return profile
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_id} if not found",
    )
