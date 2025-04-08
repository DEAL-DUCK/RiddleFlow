from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime
from services.backend.src.core.models import Task, Hackathon
from .schemas import CreateTaskSchema, TaskSchema
from services.backend.src.api_v1.hackathons.dependencies import get_hackathon

async def create_task_for_hackathon(
    session: AsyncSession,
    task_data: CreateTaskSchema,
    hackathon_id: int
) -> TaskSchema:
    hackathon = await get_hackathon(session, hackathon_id)


    task = Task(
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        hackathon_id=hackathon_id,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return TaskSchema.model_validate(task)



async def delete_task(
        task_id : int,
        session: AsyncSession
):
    task = await session.get(Task, task_id)
    if task:
        await session.delete(task)
        await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='task not found')
    return {'ok':'Task deleted'}


async def get_task_by_id(
        session: AsyncSession,
        task_id: int,
):
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found'
            )

    return task
async def get_all_tasks(
        session: AsyncSession,
):
    result = await session.execute(select(Task))
    result = result.scalars().all()
    return [TaskSchema.model_validate(task) for task in result]