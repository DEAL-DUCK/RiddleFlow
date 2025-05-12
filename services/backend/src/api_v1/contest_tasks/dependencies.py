from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user, current_active_superuser
from core.models import User, Contest, ContestUserAssociation, ContestTask
from core.models.db_helper import db_helper


async def verify_user_is_creator_or_participant(
        contest_id: int,
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter),
):
    contest = await session.get(Contest, contest_id)
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контест не найден"
        )

    if user.id == contest.creator_id or user.is_superuser:
        return user

    participation = await session.scalar(
        select(ContestUserAssociation).where(
            ContestUserAssociation.contest_id == contest_id,
            ContestUserAssociation.user_id == user.id,
        )
    )

    if participation is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь создателем или участником этого контеста"
        )

    return user


async def verify_user_is_creator_or_participant_by_task(
    task_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await session.get(ContestTask, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    contest = await session.get(Contest, task.contest_id)
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контест не найден"
        )

    if user.id == contest.creator_id or user.is_superuser:
        return user

    participation = await session.scalar(
        select(ContestUserAssociation).where(
            ContestUserAssociation.contest_id == task.contest_id,
            ContestUserAssociation.user_id == user.id,
        )
    )

    if not participation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не являетесь участником или создателем этого контеста"
        )

    return user