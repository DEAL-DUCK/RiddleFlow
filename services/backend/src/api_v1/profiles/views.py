from gc import get_referrers

from fastapi import Depends, APIRouter
from fastapi_users.schemas import model_dump
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from . import crud
from api_v1.profiles.dependencies import get_profile_by_id
from api_v1.profiles.schemas import (
    ProfileSchema,
    ProfileUpdateSchema
)
from api_v1.auth.fastapi_users import current_active_user, current_active_superuser
from core.models import db_helper, User
from .crud import get_profile_by_username
from .dependencies import get_profile_by_first_name

router = APIRouter(tags=["Профиль"])


@router.get("/", response_model=ProfileSchema)
async def get_profile(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_profile(session=session, user_id=user.id)


# для админа
@router.get(
    "/{user_id}",
    response_model=ProfileSchema,
    dependencies=[Depends(current_active_superuser)],
)
async def get_profile(
    profile: ProfileSchema = Depends(get_profile_by_id),
):
    return profile

@router.get(
    '{/username}',summary="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
async def get_public_profile(
        profile : ProfileSchema = Depends(get_profile_by_username)
):
    return profile


@router.patch("/", response_model=ProfileSchema)
async def update_profile(
    profile_update: ProfileUpdateSchema,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.update_profile(
        session=session,
        profile=user.profile,
        profile_update=profile_update,
    )
