from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from core.models import Jury, HackathonSubmission, JuryEvaluation, User
from . import schemas
from core.models.db_helper import db_helper
from . import crud
from .depends import get_evaluation_by_id, get_current_jury
from ..auth.fastapi_users import current_active_user, current_active_superuser
from ..hackathon_submissions.dependencies import check_submission_ownership, get_submission_by_id_func
from ..jurys.depends import get_jury_by_id, is_this_user_jury_this_hackathon,is_this_user_jury
from .schemas import EvaluationCreateSchema, EvaluationReadSchema, EvaluationUpdateSchema

router = APIRouter(tags=["Оценки"])

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


@router.get("/admin/")
async def get_all_evalutions(
        session : AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.get_all_evaluations(session)

@router.post(
    "/",
    response_model=EvaluationReadSchema,
)
async def create_evaluation(
    submission_id: int,
    evaluation_data: Annotated[EvaluationCreateSchema, Depends()],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    jury: Annotated[Jury, Depends(is_this_user_jury)]
) -> EvaluationReadSchema:
    submission = await session.get(HackathonSubmission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    evaluation = await crud.create_evaluation(
        session=session,
        submission_id=submission_id,
        data_in=evaluation_data,
        jury=jury
        )
    return evaluation
@router.delete("/")
async def delete_evaluation_endpoint(
    evaluation_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_jury: Jury = Depends(get_current_jury)
):
    return await crud.delete_evaluation(
        evaluation_id=evaluation_id,
        session=session,
        current_jury=current_jury
    )

@router.patch("/")
async def update_submission_endpoint(
        update_data : EvaluationUpdateSchema,
        session : AsyncSession = Depends(db_helper.session_getter),
        evalution : JuryEvaluation = Depends(get_evaluation_by_id),
        current_jury : Jury = Depends(get_current_jury),
):
    return await crud.update_evaluation(
        session=session,
        update_data=update_data,
        evaluation_id=evalution.id,
        current_jury=current_jury
    )