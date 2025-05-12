from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.fastapi_users import current_active_user
from api_v1.hackathons.dependencies import get_hackathon_by_id
from core.models import User, Hackathon, db_helper, JuryHackathonAssociation
from core.models.jury import Jury

async def get_jury_by_id(
    jury_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
):
    jury = await session.get(Jury,jury_id)
    if jury is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jury {jury_id} if not found",
        )
    return jury


async def is_this_user_jury(
        session: AsyncSession = Depends(db_helper.session_getter),
        user: User = Depends(current_active_user)
) -> Jury:
    result = await session.execute(select(Jury).where(Jury.user_id == user.id))
    jury = result.scalar_one_or_none()

    if not jury:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a jury member"
        )

    return jury
async def is_this_user_jury_this_hackathon(
        session : AsyncSession = Depends(db_helper.session_getter),
        jury: Jury = Depends(get_jury_by_id),
        hackathon : Hackathon = Depends(get_hackathon_by_id)
):
    stmt = select(
        JuryHackathonAssociation
    ).where(JuryHackathonAssociation.hackathon_id == hackathon.id).where(
        JuryHackathonAssociation.jury_id == jury.id
    )
    association = await session.execute(stmt)
    if association:
        return jury
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"жюри {jury.id} не судит этот хакатон ",
    )


