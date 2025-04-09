from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime

from core.models import hackathon
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
        task_id: int,
        session: AsyncSession
):
    task = await session.get(Task, task_id)
    if task:
        await session.delete(task)
        await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='task not found')
    return {'ok': 'Task deleted'}


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


async def get_all_task_by_hackathon(
        session: AsyncSession,
        hackathon_id: int,
):
    result = await session.execute(select(Task).where(Task.hackathon_id == hackathon_id))
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='hackathon not found')
    return tasks


async def update_task(
        session: AsyncSession,
        task_id: int,
        update_data: dict[str, Any],
) -> Task:
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')

    allowed_fields = {'title', 'description', 'task_type', 'hackathon_id'}
    invalid_fields = set(update_data.keys()) - allowed_fields
    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update fields: {', '.join(invalid_fields)}"
        )
    if 'hackathon_id' in update_data and update_data['hackathon_id'] != task.hackathon_id:
        hack = await session.get(Hackathon, update_data['hackathon_id'])
        if hack is None:
            raise HTTPException(status_code=404, detail='Hackathon not found')
        await session.delete(task)
        await session.commit()
        new_task_data = {
            'title': update_data.get('title', task.title),
            'description': update_data.get('description', task.description),
            'task_type': update_data.get('task_type', task.task_type),
        }
        await create_task_for_hackathon(
            session=session,
            task_data=CreateTaskSchema(**new_task_data),
            hackathon_id=update_data['hackathon_id']
        )

    for field, value in update_data.items():
        setattr(task, field, value)

    try:
        await session.commit()
        await session.refresh(task)
        return task
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
