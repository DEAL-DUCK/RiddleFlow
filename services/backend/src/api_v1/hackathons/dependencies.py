from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.backend.src.api_v1.hackathons.crud import (
    get_hackathon,
    get_user_in_hackathon,
)
from services.backend.src.core.models import db_helper, Hackathon, User


async def get_hackathon_by_id(
    hackathon_id: Annotated[int, Path(ge=1)],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Hackathon:
    hackathon = await get_hackathon(session=session, hackathon_id=hackathon_id)
    if hackathon is not None:
        return hackathon
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Hackathon {hackathon_id} is not found",
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
