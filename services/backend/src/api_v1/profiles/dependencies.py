from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.backend.src.api_v1.profiles.crud import get_profile
from services.backend.src.core.models.db_helper import db_helper
from services.backend.src.core.models.profile import Profile

async def get_profile_by_id(
    user_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Profile:
    profile = await get_profile(session=session, user_id=user_id)
    if profile is not None:
        return profile
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_id} if not found",
    )
