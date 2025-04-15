from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.groups.crud import get_group
from core.models import db_helper, Group


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
