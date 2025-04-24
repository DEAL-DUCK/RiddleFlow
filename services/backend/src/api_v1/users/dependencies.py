from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user
from api_v1.users.crud import get_user
from core.models import db_helper, User, Group


async def get_user_by_id(
    user_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    user = await get_user(session=session, user_id=user_id)
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user_id} if not found",
    )


async def user_is_creator(
    user: User = Depends(current_active_user),
):
    if user.user_role.value == "CREATOR" or user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not creator",
    )


async def user_is_participant(
    user: User = Depends(current_active_user),
):
    if user.user_role.value == "PARTICIPANT" or user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not participant",
    )
