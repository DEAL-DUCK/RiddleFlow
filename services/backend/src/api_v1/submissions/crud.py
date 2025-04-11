from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import HTTPException, status
from core.models import Submission, Task, HackathonUserAssociation
from .schemas import SubmissionCreate, SubmissionRead, SubmissionStatus
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any, List

not_submissions = HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def create_submission(
    session: AsyncSession,
    submission_data: SubmissionCreate
) -> Submission:
    try:
        # Проверяем существование задачи
        task_exists = await session.execute(
            select(Task).where(Task.id == submission_data.task_id)
        )
        if not task_exists.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задача не найдена"
            )

        # Проверяем, что пользователь зарегистрирован на хакатон
        hackathon_id = await session.execute(
            select(Task.hackathon_id).where(Task.id == submission_data.task_id)
        )
        hackathon_id = hackathon_id.scalar_one()

        user_registered = await session.execute(
            select(HackathonUserAssociation).where(
                HackathonUserAssociation.hackathon_id == hackathon_id,
                HackathonUserAssociation.user_id == submission_data.user_id
            )
        )
        if not user_registered.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не зарегистрирован на этот хакатон"
            )

        # Проверяем, нет ли уже решения для этой задачи от этого пользователя
        existing_submission = await session.execute(
            select(Submission).where(
                Submission.task_id == submission_data.task_id,
                Submission.user_id == submission_data.user_id
            )
        )
        if existing_submission.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Решение для этой задачи уже существует"
            )

        # Создаем новое решение
        new_submission = Submission(
            **submission_data.model_dump(),
            submitted_at=datetime.utcnow()
        )

        session.add(new_submission)
        await session.commit()
        await session.refresh(new_submission)
        return new_submission

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании решения: {str(e)}"
        )

async def get_user_submissions(session: AsyncSession, user_id: int):
    stmt = select(Submission).where(Submission.user_id == user_id)
    result = await session.execute(stmt)
    submissions = result.scalars().all()
    raise not_submissions if submissions is None else submissions


async def get_submission_by_id_func(session: AsyncSession, submission_id: int):
    stmt = select(Submission).where(Submission.id == submission_id)
    result = await session.execute(stmt)
    submission = result.scalars().first()
    raise not_submissions if submission is None else submission


async def get_submission_by_task_id_plus_user_id(
        session: AsyncSession,
        task_id: int,
        user_id: int
):
    stmt = select(Submission).where(Submission.task_id == task_id).where(Submission.user_id == user_id)
    result = await session.execute(stmt)
    submission = result.scalars().first()
    raise not_submissions if submission is None else submission


async def delete_submission_by_id(session: AsyncSession, submission_id: int):
    submission = await session.get(Submission, submission_id)
    if not submission:
        raise not_submissions
    await session.delete(submission)
    await session.commit()
    return {'ok': f' submission with id : {submission_id} deleted'}


async def all_submissions(session: AsyncSession):
    stmt = select(Submission).order_by(Submission.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_all_submissions_any_user(
        session: AsyncSession,
        user_id: int
):
    stmt = select(Submission).where(Submission.user_id == user_id)
    result = await session.execute(stmt)
    submissions = result.scalars().all()
    if not submissions:
        raise not_submissions
    for submission in submissions:
        await session.delete(submission)
    await session.commit()
    return {
        'ok': True,
        'deleted_count': len(submissions),
        'user_id': user_id
    }


async def update_submission(
        session: AsyncSession,
        submission_id: int,
        update_data: Dict[str, Any],
) -> SubmissionRead:
    result = await session.execute(
        select(Submission).where(Submission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise not_submissions
    allowed_fields = {'code_url', 'description', 'status'}
    invalid_fields = set(update_data.keys()) - allowed_fields

    if invalid_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update fields: {', '.join(invalid_fields)}"
        )

    for field, value in update_data.items():
        setattr(submission, field, value)

    if 'status' in update_data:
        if update_data['status'] == SubmissionStatus.SUBMITTED:
            submission.submitted_at = datetime.utcnow()
        elif update_data['status'] == SubmissionStatus.GRADED:
            submission.graded_at = datetime.utcnow()

    try:
        await session.commit()
        await session.refresh(submission)
        return submission
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


async def get_all_submissions_any_user_in_any_hackathon(
        session: AsyncSession,
        hackathon_id: int,
        user_id: int
):
    try:
        # Проверяем участие пользователя в хакатоне
        participation = await session.execute(
            select(HackathonUserAssociation)
            .where(
                HackathonUserAssociation.hackathon_id == hackathon_id,
                HackathonUserAssociation.user_id == user_id
            )
        )
        if not participation.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not registered for this hackathon"
            )

        # Получаем решения
        stmt = (
            select(Submission)
            .join(Submission.task)
            .where(
                Submission.user_id == user_id,
                Task.hackathon_id == hackathon_id
            )
        )

        result = await session.execute(stmt)
        submissions = result.scalars().all()

        if not submissions:
            raise not_submissions
        return [{**submission.__dict__, "hackathon_id": hackathon_id} for submission in submissions]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching submissions: {str(e)}"
        )