from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.hackathons.crud import get_hackathon
from api_v1.users.dependencies import user_is_creator, user_is_participant
from core.models import db_helper, Hackathon, User, Group, HackathonUserAssociation
from core.models.hackathon import HackathonStatus

async def get_hackathon_by_id(
    hackathon_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Hackathon:
    hackathon = await get_hackathon(session=session, hackathon_id=hackathon_id)
    if hackathon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hackathon {hackathon_id} if not found",
        )

    if hackathon.is_archived:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='hackathon archived')
    return hackathon



async def user_is_creator_of_this_hackathon(
    user: User = Depends(user_is_creator),
    hackathon: Hackathon = Depends(get_hackathon_by_id),
):
    if user.id == hackathon.creator_id or user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not creator of this hackathon",
    )


async def user_is_part_of_this_hackathon(
        hackathon: Hackathon = Depends(get_hackathon_by_id),
        user: User = Depends(user_is_participant),
        session: AsyncSession = Depends(db_helper.session_getter),
):
    stmt = select(HackathonUserAssociation).where(
        HackathonUserAssociation.hackathon_id == hackathon.id,
        HackathonUserAssociation.user_id == user.id
    )
    result = await session.execute(stmt)
    association = result.scalar_one_or_none()

    if association or user.is_superuser:
        return user

    else:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"User {user.id} is not a participant of hackathon {hackathon.id}"
    )

# async def get_user_in_hackathon_by_id(
#     user_id: Annotated[int, Path(ge=1)],
#     hackathon: Hackathon = Depends(get_hackathon_by_id),
#     session: AsyncSession = Depends(db_helper.scoped_session_dependency),
# ):
#     user = await get_user_in_hackathon(
#         session=session,
#         hackathon=hackathon,
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
