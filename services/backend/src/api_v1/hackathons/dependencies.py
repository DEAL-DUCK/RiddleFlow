from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.backend.src.api_v1.hackathons.crud import get_hackathon
from services.backend.src.core.models import db_helper, Hackathon


async def get_hackathon_by_id(
    hackathon_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Hackathon:
    hackathon = await get_hackathon(session=session, hackathon_id=hackathon_id)
    if hackathon is not None:
        return hackathon
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Hackathon {hackathon_id} if not found",
    )
