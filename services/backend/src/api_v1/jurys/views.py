from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas
from services.backend.src.core.models.db_helper import db_helper
from . import crud

router = APIRouter(tags=["Жюри"])

@router.post(
    "/add_jury_to_hackathon",
    response_model=schemas.JuryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_jury_member_to_hackathon(
    data: schemas.JuryCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.add_jury_to_hackathon(
        session=session,
        user_id=data.user_id,
        hackathon_id=data.hackathon_id,
    )
@router.delete(
    '/del_jury_from_hackathon',
)
async def del_jury_from_hackathon(
        jury_id : int,
        hackathon_id : int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await crud.remove_jury_from_hackathon(
        session=session,
        jury_id=jury_id,
        hackathon_id=hackathon_id,
    )
@router.get(
    '/get_all_hackathons_where_this_jury_work',
)
async def get_all_hackathons_where_this_jury_work(
jury_id : int,
session: AsyncSession = Depends(db_helper.scoped_session_dependency)

):
    return await crud.get_hackathons_judged_by_jury(
        session=session,
        jury_id=jury_id,
    )
