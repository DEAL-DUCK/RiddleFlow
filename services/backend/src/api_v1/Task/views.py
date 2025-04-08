from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import CreateTaskSchema, TaskSchema
from .crud import create_task_for_hackathon, get_all_tasks_in_hackathon
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
@router.get('/get_all_tasks_in_hackathon')
async def get_task_by_hackathon_id(
        hackathon_id: int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await get_all_tasks_in_hackathon(session, hackathon_id)