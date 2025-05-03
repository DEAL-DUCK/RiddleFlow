from typing import Annotated

from fastapi import Path, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
import os

from api_v1.contests.crud import get_contest
from api_v1.contests.dependencies import get_contest_by_id
from api_v1.jurys.crud import any_not
from core.config import s3_client, settings
from api_v1.auth.fastapi_users import current_active_user
from api_v1.groups.crud import get_group
from api_v1.hackathons.dependencies import get_hackathon_by_id
from api_v1.users.dependencies import user_is_participant
from core.models import db_helper, Group, User, Hackathon, Contest, JuryEvaluation, HackathonSubmission, Jury
from core.models.group import GroupStatus

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Annotated
from core.models import JuryEvaluation
from .schemas import EvaluationReadSchema



async def get_current_jury(
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        user: User = Depends(current_active_user)
) -> Jury:
    result = await session.execute(
        select(Jury)
        .where(Jury.user_id == user.id)
    )
    jury = result.scalar_one_or_none()

    if not jury:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a jury member"
        )

    return jury
async def get_evaluation_by_id(
        evaluation_id: int,
        session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        current_jury: Annotated[Jury, Depends(get_current_jury)],
        user : User = Depends(current_active_user)
) -> EvaluationReadSchema:
    result = await session.execute(
        select(JuryEvaluation)
        .where(JuryEvaluation.id == evaluation_id)
        .options(
            selectinload(JuryEvaluation.jury),
            selectinload(JuryEvaluation.submission),
            selectinload(JuryEvaluation.hackathon)
        )
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    if evaluation.jury_id != current_jury.id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this evaluation"
        )

    return EvaluationReadSchema.model_validate(evaluation)
async def get_submission_by_id_for_jury(
        session : AsyncSession,
        submission_id : int
):
    submission = await session.get(HackathonSubmission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )