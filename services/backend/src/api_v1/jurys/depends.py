from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.models import  User, Hackathon
from core.models.jury import Jury
any_not = HTTPException(status_code=status.HTTP_404_NOT_FOUND)
async def get_jury(
        session: AsyncSession,
        user_id: int,
        hackathon_id: int,
):
    hackathon = await session.get(Hackathon, hackathon_id)
    user = await session.get(User, user_id)

    if not (hackathon and user):
        raise any_not

    stmt = select(Jury).where(Jury.user_id == user_id)
    result = await session.execute(stmt)
    jury = result.scalar_one_or_none()
    return jury
