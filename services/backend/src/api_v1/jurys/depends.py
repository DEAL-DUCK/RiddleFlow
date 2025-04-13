from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

from core.models import User, Hackathon
from core.models.jury import Jury


async def get_jury(
        session: AsyncSession,
        user_id: int,
        hackathon_id: int,
):
    try:
        hackathon = await session.get(Hackathon, hackathon_id)
        user = await session.get(User, user_id)

        if not hackathon or not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hackathon or user not found"
            )

        result = await session.execute(
            select(Jury).where(Jury.user_id == user_id)
        )
        return result.scalar_one_or_none()

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


