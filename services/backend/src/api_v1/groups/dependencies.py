from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user
from api_v1.groups.crud import get_group
from api_v1.hackathons.dependencies import get_hackathon_by_id
from api_v1.users.dependencies import user_is_participant
from core.models import db_helper, Group, User, Hackathon


async def get_group_by_id(
    group_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Group:
    group = await get_group(session=session, group_id=group_id)
    if group is not None:
        return group
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Hackathon {group_id} if not found",
    )


async def user_is_owner_of_this_group(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(user_is_participant),
):
    if group.owner_id == user.id:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not owner of group",
    )


async def user_is_owner_of_this_group_or_hackathon_creator(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(current_active_user),
    hackathon: Hackathon = Depends(get_hackathon_by_id),
):
    if group.owner_id == user.id or user.id == hackathon.creator_id:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not owner of group",
    )
