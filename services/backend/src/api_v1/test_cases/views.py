from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from . import crud
from core.models.db_helper import db_helper
from api_v1.hackathons.dependencies import user_is_creator_of_this_hackathon
from .schemas import CreateTestSchema

router = APIRouter(tags=["Тесты"])


@router.post(
    "/",
)
async def create_test(
    hackathon_id: int,
    task_id: int,
    test_data: CreateTestSchema,
    user: User = Depends(user_is_creator_of_this_hackathon),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.create_test_for_hackathon(
        session=session,
        test_data=test_data,
        hackathon_id=hackathon_id,
        task_id=task_id,
    )


@router.get("/")
async def get_tests_(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await crud.get_tests(session=session)
    return result
