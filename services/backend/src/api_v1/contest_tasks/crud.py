from typing import Any


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.models import ContestTask, Contest
from core.models.contest import ContestStatus
from .schemas import CreateContestTaskSchema, ContestTaskSchema
from api_v1.contests.dependencies import get_contest


async def create_task_for_contest(
    session: AsyncSession, task_data: CreateContestTaskSchema, contest_id: int
) -> ContestTaskSchema:
    contest = await get_contest(session, contest_id)
    if contest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    task = ContestTask(
        title=task_data.title,
        description=task_data.description,
        contest_id=contest_id,
    )
    if contest.status == ContestStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='contest already begin')
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return ContestTaskSchema.model_validate(task)


async def delete_task(task_id: int, session: AsyncSession):
    task = await session.get(ContestTask, task_id)
    if task:
        await session.delete(task)
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="contest_tasks not found"
        )
    return {"ok": "contest_tasks deleted"}


async def get_task_by_id(
    session: AsyncSession,
    task_id: int,
):
    result = await session.execute(select(ContestTask).where(ContestTask.id == task_id))
    task = result.scalars().first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="contest_tasks not found"
        )

    return task


async def get_all_tasks(
    session: AsyncSession,
):
    result = await session.execute(select(ContestTask))
    result = result.scalars().all()
    return [ContestTaskSchema.model_validate(task) for task in result]


async def get_all_task_by_contest(
    session: AsyncSession,
    contest_id: int,
):
    result = await session.execute(
        select(ContestTask).where(ContestTask.contest_id == contest_id)
    )
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="contest not found"
        )
    return tasks


async def update_task(
    session: AsyncSession,
    task_id: int,
    update_data: dict[str, Any],
) -> ContestTask:
    result = await session.execute(select(ContestTask).where(ContestTask.id == task_id))
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="contest_tasks not found")

    allowed_fields = {"title", "description", "contest_id"}
    invalid_fields = set(update_data.keys()) - allowed_fields
    if invalid_fields:
        raise HTTPException(
            status_code=400, detail=f"Cannot update fields: {', '.join(invalid_fields)}"
        )

    if "contest_id" in update_data and update_data["contest_id"] != task.contest_id:
        contest_exists = await session.execute(
            select(Contest).where(Contest.id == update_data["contest_id"])
        )
        if not contest_exists.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Contest not found")

    for field, value in update_data.items():
        setattr(task, field, value)

    try:
        await session.commit()
        await session.refresh(task)
        return task
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
