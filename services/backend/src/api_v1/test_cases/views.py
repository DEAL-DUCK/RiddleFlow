from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, Contest, ContestTask
from . import crud
from core.models.db_helper import db_helper
from api_v1.hackathons.dependencies import user_is_creator_of_this_hackathon
from .schemas import CreateTestSchema
from ..contest_tasks.crud import get_contest_task_by_id
from ..contests.dependencies import user_is_creator_of_this_contest, get_inactive_contest

router = APIRouter(tags=["Тесты"])


@router.post(
    "/",
)
async def create_test(
    test_data: CreateTestSchema,
    contest : Contest = Depends(get_inactive_contest),
    task : ContestTask = Depends(get_contest_task_by_id),
    user: User = Depends(user_is_creator_of_this_contest),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.create_test_for_contest(
        session=session,
        test_data=test_data,
        contest_id=contest.id,
        task_id=task.id,
    )


@router.get("/")
async def get_tests(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    test = await crud.get_tests(session=session)
    return [
        {
            "id": result.id,
            "input": result.expected_output,
        }
        for result in test
    ]
