from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user, current_active_superuser
from core.models import User, Hackathon, HackathonUserAssociation
from core.models.db_helper import db_helper


async def verify_user_is_creator_or_participant(
        hackathon_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter),
):
    hackathon = await session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Хакатон не найден"
        )

    if user.id == hackathon.creator_id or user.is_superuser:
        return user

    participation = await session.scalar(
        select(HackathonUserAssociation).where(
            HackathonUserAssociation.hackathon_id == hackathon_id,
            HackathonUserAssociation.user_id == user.id,
        )
    )

    if participation is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь создателем или участником этого хакатона"
        )

    return user