from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from .schemas import CreateContestTaskSchema, ContestTaskSchema, ContestTaskUpdateSchema
from . import crud
from core.models.db_helper import db_helper
from api_v1.contests.dependencies import user_is_creator_of_this_contest
from api_v1.auth.fastapi_users import current_active_user, current_active_superuser

router = APIRouter(tags=["Задачи Контестов"])


@router.post(
    "/create_task",
    response_model=ContestTaskSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    contest_id: int,
    task_data: CreateContestTaskSchema,
    user: User = Depends(user_is_creator_of_this_contest),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.create_task_for_contest(
        session=session, task_data=task_data, contest_id=contest_id
    )


"""@router.get("/get_all_tasks")
async def get_all_tasks_(
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(current_active_superuser),
):
    result = await crud.get_all_tasks(session=session)
    return result"""


@router.get("/get_all_tasks_in_contest")
async def get_tasks_in_contest(
    contest_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_all_task_by_contest(session=session, contest_id=contest_id)


@router.get("/{task_id}")
async def get_task_by_id(
    task_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await crud.get_task_by_id(session=session, task_id=task_id)
    return {"id": task.id, "title": task.title, "description": task.description}


@router.delete("/{task_id}")
async def api_delete_task(
    task_id: int,
    user: User = Depends(user_is_creator_of_this_contest),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await crud.delete_task(session=session, task_id=task_id)
    return result


@router.patch("/{task_id}")
async def update_task_endpoint(
    task_id: int,
    update_data: ContestTaskUpdateSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator_of_this_contest),
):
    return await crud.update_task(
        session=session,
        task_id=task_id,
        update_data=update_data.model_dump(exclude_unset=True),
    )
