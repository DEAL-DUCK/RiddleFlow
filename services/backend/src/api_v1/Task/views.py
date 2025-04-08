from cgitb import reset

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import CreateTaskSchema, TaskSchema
from .crud import create_task_for_hackathon,delete_task,get_task_by_id,get_all_tasks
from services.backend.src.core.models import Task
from services.backend.src.core.models import db_helper

router = APIRouter(tags=["Задачи"])


@router.post(
    "/create_task",
    response_model=TaskSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    hackathon_id: int,
    task_data: CreateTaskSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await create_task_for_hackathon(
        session=session,
        task_data=task_data,
        hackathon_id=hackathon_id
    )
@router.get('/task_by_id')
async def _get_task_by_id(
        task_id : int,
        session : AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    task = await get_task_by_id(session=session, task_id=task_id)
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description
    }
@router.delete('/delete_task')
async def api_delete_task(
        task_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    result = await delete_task(session=session, task_id=task_id)
    return result
@router.get('/get_all_tasks')
async def get_all_tasks_(
        session : AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    result = await get_all_tasks(session=session)
    return result