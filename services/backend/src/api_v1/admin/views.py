from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from api_v1.users.schemas import (
    UserSchema,
    UserRead,
    UserUpdate,
)
from core.models import db_helper, User
from api_v1.auth.fastapi_users import (
    current_active_user,
    current_active_superuser,
    fastapi_users,
)


router = APIRouter(tags=["АДМИН"])

@router.get(
    "/user/",
    response_model=list[UserSchema],
    dependencies=[Depends(current_active_superuser)],
)
async def get_all_users(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_users(session=session)
@router.get(
    '/{id}',
    response_model=UserSchema,
    dependencies = [Depends(current_active_superuser)],
)
@router.get(
    '/{id}',
    response_model=UserSchema,
    dependencies=[Depends(current_active_superuser)],
)
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(db_helper.session_getter)):
    user = await crud.get_user(session=session, user_id=user_id)
    return user

@router.get("/tasks/get_all_tasks")
async def get_all_tasks_(
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(current_active_superuser),
):
    result = await crud.get_all_tasks(session=session)
    return result

@router.get(
    "/group/",
    dependencies=[Depends(current_active_superuser)],
)
async def get_groups(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_groups(session=session)

