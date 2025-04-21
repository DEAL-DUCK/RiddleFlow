from datetime import datetime
from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.models import (
    Submission,
    Task,
    HackathonUserAssociation,
)
from .schemas import (
    SubmissionCreate,
    SubmissionRead,
    SubmissionStatus,
)


async def not_submissions():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

async def create_submission(
    session: AsyncSession, submission_data: SubmissionCreate, user_id: int
) -> Submission:
    task = await session.scalar(
        select(Task).where(Task.id == submission_data.task_id)
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )

    user_registered = await session.scalar(
        select(HackathonUserAssociation).where(
            HackathonUserAssociation.hackathon_id == task.hackathon_id,
            HackathonUserAssociation.user_id == user_id,
        )
    )
    if not user_registered:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не зарегистрирован на этот хакатон",
        )

    existing_submission = await session.scalar(
        select(Submission).where(
            Submission.task_id == submission_data.task_id,
            Submission.user_id == user_id,
            Submission.description == submission_data.description,
        )
    )
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Решение для этой задачи уже существует",
        )

    submission_dict = submission_data.model_dump()
    submission_dict.pop("status", None)

    new_submission = Submission(
        **submission_dict,
        user_id=user_id,
        status=SubmissionStatus.SUBMITTED,
        submitted_at=datetime.utcnow(),
        graded_at=datetime.utcnow(),
    )

    session.add(new_submission)
    await session.commit()
    await session.refresh(new_submission)

    return new_submission


async def get_my_submissions(session: AsyncSession, user_id: int):
    stmt = select(Submission).where(Submission.user_id == user_id)
    result = await session.execute(stmt)
    submissions = result.scalars().all()
    return submissions if submissions else await not_submissions()


async def get_submission_by_id_func(session: AsyncSession, submission_id: int,user_id : int):
    stmt = select(Submission).where(Submission.id == submission_id).where(Submission.user_id == user_id)
    result = await session.execute(stmt)
    submission = result.scalars().first()
    return submission if submission else await not_submissions()


async def get_submission_by_task_id_plus_user_id(
    session: AsyncSession, task_id: int, user_id: int
):
    task_exists = await session.scalar(
        select(Task).where(Task.id == task_id).exists().select()
    )

    if not task_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id {task_id} not found"
        )
    result = await session.execute(
        select(Submission)
        .where(Submission.task_id == task_id)
        .where(Submission.user_id == user_id)
    )
    submissions = result.scalars().all()
    return submissions if submissions else await not_submissions()









async def delete_submission_by_id(session: AsyncSession, submission_id: int):
    submission = await session.get(Submission, submission_id)
    if not submission:
        await not_submissions()
    await session.delete(submission)
    await session.commit()
    return {"ok": f" submission with id : {submission_id} deleted"}


async def all_submissions(session: AsyncSession):
    stmt = select(Submission).order_by(Submission.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_all_submissions_any_user(session: AsyncSession, user_id: int):
    stmt = select(Submission).where(Submission.user_id == user_id)
    result = await session.execute(stmt)
    submissions = result.scalars().all()
    if not submissions:
        await not_submissions()
    for submission in submissions:
        await session.delete(submission)
    await session.commit()
    return {"ok": True, "deleted_count": len(submissions), "user_id": user_id}


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
        await not_submissions()
    allowed_fields = {"code_url", "description", "status"}
    invalid_fields = set(update_data.keys()) - allowed_fields

    if invalid_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update fields: {', '.join(invalid_fields)}",
        )

    for field, value in update_data.items():
        setattr(submission, field, value)

    if "status" in update_data:
        if update_data["status"] == SubmissionStatus.SUBMITTED:
            submission.submitted_at = datetime.utcnow()
        elif update_data["status"] == SubmissionStatus.GRADED:
            submission.graded_at = datetime.utcnow()

    try:
        await session.commit()
        await session.refresh(submission)
        return submission
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


# async def get_all_evaluations(
#     session: AsyncSession,
#     submission_id: int,
# ) -> List[Dict[str, any]]:
#     if not await get_submission_by_id_func(session, submission_id):
#         await not_submissions()
#
#     stmt = (
#         select(JuryEvaluation)
#         .where(JuryEvaluation.submission_id == submission_id)
#         .options(
#             load_only(
#                 JuryEvaluation.id,
#                 JuryEvaluation.score,
#                 JuryEvaluation.comment,
#                 JuryEvaluation.jury_id,
#             )
#         )
#     )
#
#     result = await session.execute(stmt)
#     evaluations = result.scalars().all()
#
#     return [
#         {
#             "id": eval.id,
#             "score": eval.score,
#             "comment": eval.comment,
#             "jury_id": eval.jury_id,
#         }
#         for eval in evaluations
#     ]
