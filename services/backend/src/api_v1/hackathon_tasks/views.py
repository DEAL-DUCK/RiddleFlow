from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, HackathonTask
from .dependencies import verify_user_is_creator_or_participant, verify_user_is_creator_or_participant_by_task
from .schemas import (
    CreateHackathonTaskSchema,
    HackathonTaskSchema,
    HackathonTaskUpdateSchema,
)
from . import crud
from core.models.db_helper import db_helper
from api_v1.hackathons.dependencies import user_is_creator_of_this_hackathon
from api_v1.auth.fastapi_users import current_active_user, current_active_superuser

router = APIRouter(tags=["Задачи Хакатонов"])

@router.post(
    "/create_task",
    response_model=HackathonTaskSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    hackathon_id: int,
    task_data: CreateHackathonTaskSchema,
    user: User = Depends(user_is_creator_of_this_hackathon),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.create_task_for_hackathon(
        session=session,
        task_data=task_data,
        hackathon_id=hackathon_id
    )

@router.get(
    "/get_all_tasks_in_hackathon",
    response_model=list[HackathonTaskSchema]
)
async def get_tasks_in_hackathon(
    hackathon_id: int,
    user: User = Depends(verify_user_is_creator_or_participant),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    tasks = await crud.get_all_task_by_hackathon(
        session=session,
        hackathon_id=hackathon_id
    )
    return [HackathonTaskSchema.model_validate(task) for task in tasks]

@router.get(
    "/{task_id}",
    response_model=HackathonTaskSchema
)
async def get_task_by_id(
    task_id: int,
    user: User = Depends(verify_user_is_creator_or_participant_by_task),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await crud.get_task_by_id(session=session, task_id=task_id)
    return HackathonTaskSchema.model_validate(task)

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def api_delete_task(
    task_id: int,
    user: User = Depends(user_is_creator_of_this_hackathon),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    await crud.delete_task(session=session, task_id=task_id)

@router.patch(
    "/{task_id}",
    response_model=HackathonTaskSchema
)
async def update_task_endpoint(
    task_id: int,
    update_data: HackathonTaskUpdateSchema,
    user: User = Depends(user_is_creator_of_this_hackathon),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await crud.update_task(
        session=session,
        task_id=task_id,
        update_data=update_data.model_dump(exclude_unset=True),
    )
    return HackathonTaskSchema.model_validate(task)