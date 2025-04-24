from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import user_is_creator
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
from ..hackathons.schemas import HackathonSchema

router = APIRouter(tags=["Пользователь"])



router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)

# @router.get("/{user_id}", response_model=UserSchema)
# async def get_user(user: UserSchema = Depends(get_user_by_id)):
#     return user


# @router.post("/", response_model=UserSchema)
# async def create_user(
#     user_in: UserCreateSchema,
#     session: AsyncSession = Depends(db_helper.session_getter),
# ):
#     return await crud.create_user(session=session, user_in=user_in)

@router.get("/admin/{'sd'}")
async def admin_user(
    user : User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.for_ivan_func(session=session,user_id=user.id)