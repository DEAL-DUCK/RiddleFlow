from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user
from api_v1.contest_submissions.crud import not_submissions
from core.models import User, HackathonSubmission, db_helper
from core.models.hackathon_submission import SubmissionStatus


async def user_is_participant_or_admin(
    user: User = Depends(current_active_user),
):
    if user.user_role.value == "PARTICIPANT" or user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not participant",
    )


async def check_submission_ownership(
    submission_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    submission = await session.get(HackathonSubmission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
        )
    if user.id != submission.user_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this submission",
        )
    return submission
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
"""async def check_for_submission_submitted(
        session: AsyncSession,
        submission : HackathonSubmission = Depends(get_submission_by_id_func),
):
    if submission.status == SubmissionStatus.SUBMITTED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='submission not send')
    return submission"""