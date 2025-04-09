from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import HTTPException, status
from core.models import Submission
from .schemas import SubmissionCreate, SubmissionRead


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
async def get_submission_by_id_plus_user_id(
        session: AsyncSession,
        submission_id: int,
        user_id: int
):
    stmt = select(Submission).where(Submission.id == submission_id).where(Submission.user_id == user_id)
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


