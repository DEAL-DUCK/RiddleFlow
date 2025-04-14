from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from api_v1.users.schemas import (
    UserSchema,
    UserRead,
    UserUpdate,
)
from core.models import db_helper
from api_v1.auth.fastapi_users import fastapi_users


router = APIRouter(tags=["Пользователь"])


@router.get("/", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_users(session=session)


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
