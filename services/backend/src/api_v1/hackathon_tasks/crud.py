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
    existing_task = await session.execute(
        select(HackathonTask)
        .where(
            HackathonTask.hackathon_id == hackathon_id,
            HackathonTask.title == task_data.title
        )
    )
    if existing_task.scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Задача с таким названием уже существует в этом хакатоне"
        )

    existing_description = await session.execute(
        select(HackathonTask)
        .where(
            HackathonTask.hackathon_id == hackathon_id,
            HackathonTask.description == task_data.description
        )
    )
    if existing_description.scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Задача с таким описанием уже существует в этом хакатоне"
        )
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
    hackathon = await get_hackathon(session,task.hackathon_id)
    if hackathon.status == 'ACTIVE':
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='hackathon active')
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
    task = await session.get(HackathonTask,task_id)
    if task.is_archived :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail='task archived')
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
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
        raise HTTPException(status_code=404, detail="Задача не найдена")

    hackathon = await session.get(Hackathon, task.hackathon_id)
    if hackathon.status == HackathonStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Нельзя изменять задачи активного хакатона"
        )
    allowed_fields = {"title", "description", "task_type", "hackathon_id", "max_attempts"}
    invalid_fields = set(update_data.keys()) - allowed_fields

    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Невозможно обновить поля: {', '.join(invalid_fields)}"
        )

    if "max_attempts" in update_data:
        new_max_attempts = update_data["max_attempts"]
        if not isinstance(new_max_attempts, int) or new_max_attempts < 1:
            raise HTTPException(
                status_code=400,
                detail="max_attempts должно быть целым числом больше 0"
            )
        if new_max_attempts < task.current_attempts:
            raise HTTPException(
                status_code=400,
                detail=f"Новый лимит попыток ({new_max_attempts}) меньше текущего количества решений ({task.current_attempts})"
            )

    if "hackathon_id" in update_data and update_data["hackathon_id"] != task.hackathon_id:
        hackathon_exists = await session.execute(
            select(Hackathon).where(Hackathon.id == update_data["hackathon_id"])
        )
        if not hackathon_exists.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Хакатон не найден")

    for field, value in update_data.items():
        setattr(task, field, value)

    try:
        await session.commit()
        await session.refresh(task)
        return task
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
async def archive(session:AsyncSession,task:HackathonTask):
    if task.hackathon.status == HackathonStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'хакатон уже идет')
    task.is_archived = True
    await session.commit()
    return {'ok':f'task {task.id} is archived'}
async def unarchive(session:AsyncSession,task:HackathonTask):
    task.is_archived = False
    await session.commit()
    return {'ok':f'task {task.id} is unarchived'}
