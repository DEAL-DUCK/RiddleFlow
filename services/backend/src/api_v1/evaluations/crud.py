from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from core.models import JuryEvaluation, Submission, Jury, JuryHackathonAssociation
from core.models.submission import SubmissionStatus
from .schemas import EvaluationSchema, EvaluationsUpdateSchema
from ..jurys.crud import any_not
from api_v1.submissions.views import create_submission


async def create_evaluation(
        session: AsyncSession,
        submission_id: int,
        jury_id: int,
        comment: str,
        score: float,
) -> EvaluationSchema:
    try:
        submission = await session.scalar(
            select(Submission)
            .options(selectinload(Submission.task))
            .where(Submission.id == submission_id)
        )
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        jury = await session.scalar(select(Jury).where(Jury.id == jury_id))
        if not jury:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jury not found"
            )

        is_assigned = await session.scalar(
            select(JuryHackathonAssociation)
            .where(and_(
                JuryHackathonAssociation.jury_id == jury_id,
                JuryHackathonAssociation.hackathon_id == submission.task.hackathon_id
            ))
        )
        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Jury is not assigned to this hackathon"
            )
        if submission.status not in [SubmissionStatus.SUBMITTED, SubmissionStatus.DRAFT]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only evaluate SUBMITTED or DRAFT submissions"
            )
        if not (0 <= score <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score must be between 0 and 100"
            )

        existing_eval = await session.scalar(
            select(JuryEvaluation)
            .where(and_(
                JuryEvaluation.jury_id == jury_id,
                JuryEvaluation.submission_id == submission_id
            ))
        )

        if existing_eval:
            existing_eval.score = score
            existing_eval.comment = comment
            evaluation = existing_eval
        else:
            evaluation = JuryEvaluation(
                jury_id=jury_id,
                submission_id=submission_id,
                score=score,
                comment=comment
            )
            session.add(evaluation)

        submission.status = SubmissionStatus.GRADED
        submission.graded_at = func.now()

        await session.commit()
        await session.refresh(evaluation)

        return EvaluationSchema(
            jury_id=evaluation.jury_id,
            submission_id=evaluation.submission_id,
            score=evaluation.score,
            comment=evaluation.comment,
            created_at=evaluation.created_at
        )

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database integrity error: {str(e)}"
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


async def delete_evaluation(
        session: AsyncSession,
        evaluation_id: int,
):
    try:
        evaluation = await session.scalar(
            select(JuryEvaluation)
            .options(
                selectinload(JuryEvaluation.submission).selectinload(Submission.evaluations)
            )
            .where(JuryEvaluation.id == evaluation_id)
        )

        if not evaluation:
            return await any_not('evaluation')
        submission = evaluation.submission
        await session.delete(evaluation)
        remaining_evaluations = len(submission.evaluations) - 1
        if remaining_evaluations == 0:
            submission.status = SubmissionStatus.SUBMITTED
            submission.graded_at = None
            new_status = "SUBMITTED"
        else:
            new_status = submission.status.value

        await session.commit()
        return {'ok': True, 'new_status': new_status}

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении оценки: {str(e)}"
        )


async def update_evaluation(
        session: AsyncSession,
        evaluation_id: int,
        update_data: EvaluationsUpdateSchema,
):
    if await session.get(JuryEvaluation, evaluation_id) is None: return await any_not('evaluation')
    evaluation = await session.get(JuryEvaluation, evaluation_id)
    if not (0 <= update_data.score <= 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Оценка должна быть в диапазоне от 0 до 100"
        )

    evaluation.score = update_data.score
    evaluation.comment = update_data.comment

    evaluation.created_at = func.now()

    session.add(evaluation)
    await session.commit()
    await session.refresh(evaluation)
    return {
        'success': True,
        'message': 'Оценка успешно обновлена',
        'evaluation': evaluation
    }
