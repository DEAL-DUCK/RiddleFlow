from fastapi import APIRouter, Depends, status
from .schemas import CreateTaskSchema, TaskSchema, TaskUpdateSchema
from .crud import *
from core.models.db_helper import db_helper

router = APIRouter(tags=["Задачи"])


@router.post(
    "/create_task", response_model=TaskSchema, status_code=status.HTTP_201_CREATED
)
async def create_task(
    hackathon_id: int,
    task_data: CreateTaskSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await create_task_for_hackathon(
        session=session, task_data=task_data, hackathon_id=hackathon_id
    )


@router.get("/task_by_id")
async def _get_task_by_id(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    task = await get_task_by_id(session=session, task_id=task_id)
    return {"id": task.id, "title": task.title, "description": task.description}


@router.delete("/delete_task")
async def api_delete_task(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await delete_task(session=session, task_id=task_id)
    return result


@router.get("/get_all_tasks")
async def get_all_tasks_(session: AsyncSession = Depends(db_helper.session_getter)):
    result = await get_all_tasks(session=session)
    return result


@router.get("/get_all_tasks_in_hackathon")
async def get_tasks_in_hackathon(
    hackathon_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_all_task_by_hackathon(session=session, hackathon_id=hackathon_id)


@router.patch("/update_task")
async def update_task_endpoint(
    task_id: int,
    update_data: TaskUpdateSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await update_task(
        session=session,
        task_id=task_id,
        update_data=update_data.model_dump(exclude_unset=True),
    )
