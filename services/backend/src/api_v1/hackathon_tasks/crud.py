from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.models import HackathonTask, Hackathon
from core.models.hackathon import HackathonStatus
from .schemas import CreateHackathonTaskSchema, HackathonTaskSchema
from api_v1.hackathons.dependencies import get_hackathon


async def create_task_for_hackathon(
    session: AsyncSession, task_data: CreateHackathonTaskSchema, hackathon_id: int
) -> HackathonTaskSchema:
    hackathon = await get_hackathon(session, hackathon_id)
    if hackathon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if hackathon.status == HackathonStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='hackathon already begin')
    task = HackathonTask(
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        hackathon_id=hackathon_id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return HackathonTaskSchema.model_validate(task)


async def delete_task(task_id: int, session: AsyncSession):
    task = await session.get(HackathonTask, task_id)
    if task:
        await session.delete(task)
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="hackathon_tasks not found"
        )
    return {"ok": "hackathon_tasks deleted"}


async def get_task_by_id(
    session: AsyncSession,
    task_id: int,
):
    result = await session.execute(
        select(HackathonTask).where(HackathonTask.id == task_id)
    )
    task = result.scalars().first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="hackathon_tasks not found"
        )

    return task


async def get_all_tasks(
    session: AsyncSession,
):
    result = await session.execute(select(HackathonTask))
    result = result.scalars().all()
    return [HackathonTaskSchema.model_validate(task) for task in result]


async def get_all_task_by_hackathon(
    session: AsyncSession,
    hackathon_id: int,
):
    result = await session.execute(
        select(HackathonTask).where(HackathonTask.hackathon_id == hackathon_id)
    )
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="hackathon not found"
        )
    return tasks


async def update_task(
    session: AsyncSession,
    task_id: int,
    update_data: dict[str, Any],
) -> HackathonTask:
    result = await session.execute(
        select(HackathonTask).where(HackathonTask.id == task_id)
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="hackathon_tasks not found")

    allowed_fields = {"title", "description", "task_type", "hackathon_id"}
    invalid_fields = set(update_data.keys()) - allowed_fields
    if invalid_fields:
        raise HTTPException(
            status_code=400, detail=f"Cannot update fields: {', '.join(invalid_fields)}"
        )

    if (
        "hackathon_id" in update_data
        and update_data["hackathon_id"] != task.hackathon_id
    ):
        hackathon_exists = await session.execute(
            select(Hackathon).where(Hackathon.id == update_data["hackathon_id"])
        )
        if not hackathon_exists.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Hackathon not found")

    for field, value in update_data.items():
        setattr(task, field, value)

    try:
        await session.commit()
        await session.refresh(task)
        return task
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
