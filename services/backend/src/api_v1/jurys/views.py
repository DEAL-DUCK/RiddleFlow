from fastapi import HTTPException, APIRouter, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from . import crud
from core.models import User, Hackathon
from core.models.db_helper import db_helper
from core.models.jury import Jury

router = APIRouter(tags=["Жюри"])


@router.post("/{add}")
async def add_jury(
        user_id : int,
        hackathon_id : int,
        session : AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await crud.add_jury_in_hack(
        user_id=user_id,
        session=session,
        hackathon_id=hackathon_id
    )
@router.delete("/{del_in_hack}")
async def delete_jury(
        user_id : int,
        hackathon_id : int,
        session : AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await crud.delete_jury_in_hack(
        session=session,
        hackathon_id=hackathon_id,
        user_id = user_id
    )