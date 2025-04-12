from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from services.backend.src.api_v1.profiles.dependencies import get_profile_by_id
from services.backend.src.api_v1.profiles.schemas import (
    ProfileSchema,
    ProfileUpdateSchema,
)
from services.backend.src.core.models.db_helper import db_helper

router = APIRouter(tags=["Профиль"])


@router.get("/{user_id}", response_model=ProfileSchema)
async def get_profile(profile: ProfileSchema = Depends(get_profile_by_id)):
    return profile


@router.patch("/{user_id}", response_model=ProfileSchema)
async def update_profile(
    profile_update: ProfileUpdateSchema,
    profile: ProfileSchema = Depends(get_profile_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_profile(
        session=session,
        profile=profile,
        profile_update=profile_update,
    )
