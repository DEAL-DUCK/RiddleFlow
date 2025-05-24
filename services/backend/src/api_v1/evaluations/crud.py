from datetime import datetime
from sqlalchemy import select, and_, func, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends
from core.models import JuryEvaluation, HackathonSubmission, Jury, JuryHackathonAssociation, db_helper
from core.models.hackathon_submission import SubmissionStatus
from core.models.hackathon import HackathonStatus, Hackathon
from .depends import get_current_jury
from .schemas import  EvaluationCreateSchema,EvaluationReadSchema,EvaluationUpdateSchema
from ..jurys.crud import any_not
from api_v1.hackathon_submissions.views import submissions_create
from ..jurys.depends import get_jury_by_id, is_this_user_jury_this_hackathon, is_this_user_jury


async def create_evaluation(
    submission_id: int,
    data_in: EvaluationCreateSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
    jury: Jury = Depends(is_this_user_jury)
) -> EvaluationReadSchema:
    submission = await session.get(HackathonSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Submission not found')

    await session.refresh(submission, ["task"])
    if not submission.task:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submission has no associated task")

    existing_eval = await session.execute(
        select(JuryEvaluation)
        .where(JuryEvaluation.jury_id == jury.id, JuryEvaluation.submission_id == submission.id)
    )
    if existing_eval.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already evaluated this submission")
    is_jury_for_hackathon = await session.execute(
        select(exists().where(
            JuryHackathonAssociation.jury_id == jury.id,
            JuryHackathonAssociation.hackathon_id == submission.task.hackathon_id
        ))
    )
    if not is_jury_for_hackathon.scalar():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не назначены жюри на этот хакатон"
        )
    if submission.task.hackathon.status != 'ACTIVE':
        raise 'хакатон еще не начался'

    evaluation = JuryEvaluation(
        **data_in.model_dump(),
        submission_id=submission.id,
        jury_id=jury.id,
        hackathon_id=submission.task.hackathon_id
    )

    session.add(evaluation)
    submission.status = SubmissionStatus.SUBMITTED
    await session.commit()
    await session.refresh(evaluation)
    return EvaluationReadSchema.model_validate(evaluation)
async def delete_evaluation(
    evaluation_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_jury: Jury = Depends(get_current_jury)
) -> dict:
    evaluation = await session.get(JuryEvaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
    if evaluation.hackathon.status != 'ACTIVE':
        raise HTTPException(detail='хакатон еще не начался',status_code=status.HTTP_409_CONFLICT)
    if evaluation.jury_id != current_jury.id and not current_jury.user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this evaluation")

    await session.delete(evaluation)
    await session.commit()
    return {"message": "Evaluation deleted successfully"}


async def update_evaluation(
        evaluation_id: int,
        update_data: EvaluationUpdateSchema,
        session: AsyncSession = Depends(db_helper.session_getter),
        current_jury: Jury = Depends(get_current_jury)
) -> EvaluationReadSchema:
    evaluation = await session.execute(
        select(JuryEvaluation)
        .options(selectinload(JuryEvaluation.hackathon))
        .where(JuryEvaluation.id == evaluation_id)
    )
    evaluation = evaluation.scalar_one_or_none()
    if evaluation.hackathon.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update evaluations for active hackathons"
        )
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
    if evaluation.jury_id != current_jury.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this evaluation")
    if evaluation.hackathon.status == HackathonStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='hackathon complited')
    if update_data.score > 10 or update_data.score <= 0:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='оценка должна быть больше 0')
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(evaluation, field, value)
    evaluation.updated_at = datetime.now()
    await session.commit()
    await session.refresh(evaluation)
    return EvaluationReadSchema.model_validate(evaluation)
async def get_all_evaluations(
    session: AsyncSession
) -> list[EvaluationReadSchema]:
    result = await session.execute(
        select(JuryEvaluation)
        .options(
            selectinload(JuryEvaluation.jury),
            selectinload(JuryEvaluation.submission),
            selectinload(JuryEvaluation.hackathon)
        )
    )
    evaluations = result.scalars().all()
    return [EvaluationReadSchema.model_validate(e) for e in evaluations]