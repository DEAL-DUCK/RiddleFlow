from datetime import datetime
from typing import Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core.models import (
    HackathonSubmission,
    HackathonTask,
    HackathonUserAssociation, User, Hackathon,
)
from core.models.hackathon import HackathonStatus
from .schemas import (
    HackathonSubmissionCreate,
    HackathonSubmissionRead,
    HackathonSubmissionStatus,
)


async def not_submissions():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def create_submission(
    session: AsyncSession, submission_data: HackathonSubmissionCreate, user_id: int
) -> HackathonSubmission:
    task = await session.scalar(
        select(HackathonTask).where(HackathonTask.id == submission_data.task_id)
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
    user = await session.get(User,user_id)
    if not user_registered and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не зарегистрирован на этот хакатон",
        )
    hackathon = await session.scalar(
        select(Hackathon).where(Hackathon.id == task.hackathon_id)
    )
    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Хакатон не найден"
        )

    if hackathon.status != HackathonStatus.ACTIVE and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Решения можно отправлять только в активных хакатонах"
        )

    existing_submission = await session.scalar(
        select(HackathonSubmission).where(
            HackathonSubmission.task_id == submission_data.task_id,
            HackathonSubmission.user_id == user_id,
            HackathonSubmission.description == submission_data.description,
        )
    )
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Решение для этой задачи уже существует",
        )


    submission_dict = submission_data.model_dump()
    submission_dict.pop("status", None)

    new_submission = HackathonSubmission(
        **submission_dict,
        user_id=user_id,
        status=HackathonSubmissionStatus.SUBMITTED,
        submitted_at=datetime.utcnow(),
        graded_at=datetime.utcnow(),
    )

    session.add(new_submission)
    await session.commit()
    await session.refresh(new_submission)

    return new_submission


async def get_my_submissions(session: AsyncSession, user_id: int):
    stmt = select(HackathonSubmission).where(HackathonSubmission.user_id == user_id)
    result = await session.execute(stmt)
    submissions = result.scalars().all()
    return submissions if submissions else await not_submissions()


async def get_submission_by_id_func(
    session: AsyncSession, submission_id: int, user_id: int
):
    stmt = (
        select(HackathonSubmission)
        .where(HackathonSubmission.id == submission_id)
        .where(HackathonSubmission.user_id == user_id)
    )
    result = await session.execute(stmt)
    submission = result.scalars().first()
    return submission if submission else await not_submissions()


async def get_submission_by_task_id_plus_user_id(
    session: AsyncSession, task_id: int, user_id: int
):
    task_exists = await session.scalar(
        select(HackathonTask).where(HackathonTask.id == task_id).exists().select()
    )

    if not task_exists:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    result = await session.execute(
        select(HackathonSubmission)
        .where(HackathonSubmission.task_id == task_id)
        .where(HackathonSubmission.user_id == user_id)
    )
    submissions = result.scalars().all()
    return submissions if submissions else await not_submissions()


async def delete_submission_by_id(session: AsyncSession, submission_id: int):
    submission = await session.get(HackathonSubmission, submission_id)
    if not submission:
        await not_submissions()
    await session.delete(submission)
    await session.commit()
    return {"ok": f" submission with id : {submission_id} deleted"}


async def all_submissions(session: AsyncSession):
    stmt = select(HackathonSubmission).order_by(HackathonSubmission.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_all_submissions_any_user(session: AsyncSession, user_id: int):
    stmt = select(HackathonSubmission).where(HackathonSubmission.user_id == user_id)
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
) -> HackathonSubmissionRead:
    result = await session.execute(
        select(HackathonSubmission).where(HackathonSubmission.id == submission_id)
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
        if update_data["status"] == HackathonSubmissionStatus.SUBMITTED:
            submission.submitted_at = datetime.utcnow()
        elif update_data["status"] == HackathonSubmissionStatus.GRADED:
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


async def get_all_submissions_current_user_in_any_hackathon(
    session: AsyncSession,
    user: User,
    hackathon: Hackathon,
) -> list[dict]:
    query = (
        select(HackathonSubmission)
        .join(HackathonSubmission.task)
        .where(
            HackathonSubmission.user_id == user.id,
            HackathonTask.hackathon_id == hackathon.id
        )
        .order_by(HackathonSubmission.submitted_at.desc())
    )

    result = await session.execute(query)
    submissions = result.scalars().all()

    return [
        {
            "id": submission.id,
            "status": submission.status.value,
            "code_url": submission.code_url,
            "task_id": submission.task_id,
            "user_id": submission.user_id,
            "description": submission.description,
            "submitted_at": submission.submitted_at.isoformat(),
            "graded_at": submission.graded_at.isoformat(),
        }
        for submission in submissions
    ]

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
