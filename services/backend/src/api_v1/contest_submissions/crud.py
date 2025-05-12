from datetime import datetime
from typing import Dict, Any


from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tasks.celery_app import check_code
from core.models import (
    ContestSubmission,
    ContestTask,
    ContestUserAssociation,
)
from .schemas import (
    ContestSubmissionCreate,
    ContestSubmissionRead,
    ContestSubmissionStatus,
)


async def not_submissions():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def create_submission(
    session: AsyncSession, submission_data: ContestSubmissionCreate, user_id: int
) -> Dict[str, Any]:
    """
    Create new submission and start code checking process.
    Returns submission details with task information.
    """
    # Verify task exists
    task = await session.scalar(
        select(ContestTask).where(ContestTask.id == submission_data.task_id)
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    # Verify user is registered for the contest
    user_registered = await session.scalar(
        select(ContestUserAssociation).where(
            ContestUserAssociation.contest_id == task.contest_id,
            ContestUserAssociation.user_id == user_id,
        )
    )
    if not user_registered:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered for this contest",
        )

    # Create new submission
    new_submission = ContestSubmission(
        **submission_data.model_dump(exclude={"status"}),
        user_id=user_id,
        status="SUBMITTED",
        submitted_at=datetime.utcnow(),
    )

    session.add(new_submission)
    await session.commit()
    await session.refresh(new_submission)

    # Start async checking process
    celery_task = check_code(new_submission.id)

    return celery_task


async def get_my_submissions(session: AsyncSession, user_id: int):
    stmt = select(ContestSubmission).where(ContestSubmission.user_id == user_id)
    result = await session.execute(stmt)
    submissions = result.scalars().all()
    return submissions if submissions else await not_submissions()


async def get_submission_by_id_func(
    session: AsyncSession, submission_id: int, user_id: int
):
    stmt = (
        select(ContestSubmission)
        .where(ContestSubmission.id == submission_id)
        .where(ContestSubmission.user_id == user_id)
    )
    result = await session.execute(stmt)
    submission = result.scalars().first()
    return submission if submission else await not_submissions()


async def get_submission_by_task_id_plus_user_id(
    session: AsyncSession, task_id: int, user_id: int
):
    task_exists = await session.scalar(
        select(ContestTask).where(ContestTask.id == task_id).exists().select()
    )

    if not task_exists:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    result = await session.execute(
        select(ContestSubmission)
        .where(ContestSubmission.task_id == task_id)
        .where(ContestSubmission.user_id == user_id)
    )
    submissions = result.scalars().all()
    return submissions if submissions else await not_submissions()


async def delete_submission_by_id(session: AsyncSession, submission_id: int):
    submission = await session.get(ContestSubmission, submission_id)
    if not submission:
        await not_submissions()
    await session.delete(submission)
    await session.commit()
    return {"ok": f" submission with id : {submission_id} deleted"}


async def all_submissions(session: AsyncSession):
    stmt = select(ContestSubmission).order_by(ContestSubmission.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_all_submissions_any_user(session: AsyncSession, user_id: int):
    stmt = select(ContestSubmission).where(ContestSubmission.user_id == user_id)
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
) -> ContestSubmissionRead:
    result = await session.execute(
        select(ContestSubmission).where(ContestSubmission.id == submission_id)
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
        if update_data["status"] == ContestSubmissionStatus.SUBMITTED:
            submission.submitted_at = datetime.utcnow()
        elif update_data["status"] == ContestSubmissionStatus.GRADED:
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
