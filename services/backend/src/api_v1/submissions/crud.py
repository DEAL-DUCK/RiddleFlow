from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import HTTPException, status
from core.models import Submission
from .schemas import SubmissionCreate, SubmissionRead, SubmissionStatus


async def create_submission(
        session: AsyncSession,
        submission_data: SubmissionCreate
) -> Submission:
    """Создание нового решения с валидацией"""
    try:
        # Создаем объект решения
        new_submission = Submission(
            **submission_data.model_dump(),
            submitted_at=datetime.utcnow()
        )

        session.add(new_submission)
        await session.commit()
        await session.refresh(new_submission)
        return new_submission

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
    if not submissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No submissions found for this user"
        )

    return submissions
async def get_submission_by_id_func(session: AsyncSession, submission_id: int):
    stmt = select(Submission).where(Submission.id == submission_id)
    result = await session.execute(stmt)
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='submission not found')
    return submission
async def get_submission_by_task_id_plus_user_id(
        session: AsyncSession,
        task_id: int,
        user_id: int
):
    stmt = select(Submission).where(Submission.task_id == task_id).where(Submission.user_id == user_id)
    result = await session.execute(stmt)
    submission = result.scalars().first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='submission not found for this user')
    return submission
async def delete_submission_by_id(session: AsyncSession, submission_id: int):
    submission = await session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='submission not found')
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='submission not found')
    for submission in submissions:
        await session.delete(submission)
    await session.commit()
    return {
            'ok': True,
            'deleted_count': len(submissions),
            'user_id': user_id
        }
async def update_submission_by_id(session: AsyncSession, submission_id: int, data: SubmissionRead):
    submission = await session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='submission not found')


from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission with ID {submission_id} not found"
        )

    allowed_fields = {'code_url', 'description', 'status'}
    invalid_fields = set(update_data.keys()) - allowed_fields

    if invalid_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update fields: {', '.join(invalid_fields)}"
        )

    # 4. Применяем обновления
    for field, value in update_data.items():
        setattr(submission, field, value)

    # 5. Обновляем временные метки
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
