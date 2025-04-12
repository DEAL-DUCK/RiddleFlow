from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from core.models import JuryEvaluation, Submission, Jury, JuryHackathonAssociation
from core.models.submission import SubmissionStatus
from .schemas import EvaluationSchema


async def create_evaluation(
        session: AsyncSession,
        submission_id: int,
        jury_id: int,
        comment: str,
        score: float,
) -> EvaluationSchema:
    try:
        # Проверяем существование submission с предзагрузкой задачи
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

        # Проверяем существование жюри
        jury = await session.scalar(select(Jury).where(Jury.id == jury_id))
        if not jury:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Jury not found"
            )

        # Проверяем назначение жюри на хакатон
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

        # Проверяем статус submission
        if submission.status not in [SubmissionStatus.SUBMITTED, SubmissionStatus.DRAFT]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only evaluate SUBMITTED or DRAFT submissions"
            )

        # Проверяем диапазон оценки
        if not (0 <= score <= 100):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score must be between 0 and 100"
            )

        # Проверяем существующую оценку
        existing_eval = await session.scalar(
            select(JuryEvaluation)
            .where(and_(
                JuryEvaluation.jury_id == jury_id,
                JuryEvaluation.submission_id == submission_id
            ))
        )

        if existing_eval:
            # Обновляем существующую оценку
            existing_eval.score = score
            existing_eval.comment = comment
            evaluation = existing_eval
        else:
            # Создаем новую оценку
            evaluation = JuryEvaluation(
                jury_id=jury_id,
                submission_id=submission_id,
                score=score,
                comment=comment
            )
            session.add(evaluation)

        # Обновляем статус submission
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