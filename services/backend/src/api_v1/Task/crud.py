from sqlalchemy import select, Result

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


from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_tasks_in_hackathon(
        session: AsyncSession,
        hackathon_id: int
) -> List[TaskSchema]:
    stmt = select(Task).where(Task.hackathon_id == hackathon_id)
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    tasks = [TaskSchema.model_validate(task) for task in tasks]
    if len(tasks) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND
                            , detail='Hackathon not found')
    return tasks