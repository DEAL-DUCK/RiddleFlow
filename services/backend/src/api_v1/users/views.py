from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud
from services.backend.src.api_v1.users.dependencies import get_user_by_id
from services.backend.src.api_v1.users.schemas import (
    UserSchema,
    UserCreateSchema,
)
from services.backend.src.core.models import db_helper

router = APIRouter()


@router.get("/", response_model=list[UserSchema])
async def get_users(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_users(session=session)


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user: UserSchema = Depends(get_user_by_id)):
    return user


@router.post("/", response_model=UserSchema)
async def create_user(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_user(session=session, user_in=user_in)
