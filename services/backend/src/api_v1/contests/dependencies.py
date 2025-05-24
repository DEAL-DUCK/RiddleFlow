from typing import Annotated


from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.contests.crud import get_contest
from api_v1.users.dependencies import user_is_creator
from core.models import db_helper, Contest, User, Group
from core.models.contest import ContestStatus


async def get_contest_by_id(
    contest_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Contest:
    contest = await get_contest(session=session, contest_id=contest_id)
    if contest.is_archived :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='contest archived')
    if contest is not None:
        return contest
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Contest {contest_id} if not found",
    )


async def user_is_creator_of_this_contest(
    user: User = Depends(user_is_creator),
    contest: Contest = Depends(get_contest_by_id),
):
    if user.id == contest.creator_id or user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not creator of this contest",
    )
def get_active_contest(
        contest : Contest = Depends(get_contest_by_id),
):
    if contest.status != 'ACTIVE':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='контест еще не активен')
    return contest
def get_inactive_contest(
        contest : Contest = Depends(get_contest_by_id),
):
    if contest.status == 'PLANNED' or contest.status == 'INACTIVE':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='контест  активен')
    return contest
# async def get_user_in_contest_by_id(
#     user_id: Annotated[int, Path(ge=1)],
#     contest: Contest = Depends(get_contest_by_id),
#     session: AsyncSession = Depends(db_helper.scoped_session_dependency),
# ):
#     user = await get_user_in_contest(
#         session=session,
#         contest=contest,
#         user_id=user_id,
#     )
#
#     if user is not None:
#         return user
#
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"User {user_id} is not found",
#     )
