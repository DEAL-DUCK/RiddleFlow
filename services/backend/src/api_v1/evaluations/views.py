from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas
from services.backend.src.core.models.db_helper import db_helper
from . import crud

router = APIRouter(tags=["Оценки"])

@router.post(
    '/create',
    response_model=schemas.EvaluationSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_evaluation(
    data_in: schemas.EvaluationSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    try:
        return await crud.create_evaluation(
            session=session,
            submission_id=data_in.submission_id,
            jury_id=data_in.jury_id,
            score=data_in.score,
            comment=data_in.comment,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )