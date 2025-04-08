from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.olympiads.crud import get_olympiad
from core.models import db_helper, Olympiad


async def get_olympiad_by_id(
    olympiad_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Olympiad:
    olympiad = await get_olympiad(session=session, olympiad_id=olympiad_id)
    if olympiad is not None:
        return olympiad
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Olympiad {olympiad_id} if not found",
    )
