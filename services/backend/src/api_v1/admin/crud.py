from fastapi import HTTPException
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.tasks.schemas import TaskSchema
from core.models import User, Task, Group


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)
async def get_user(session: AsyncSession, user_id: int) -> User | None:
    if await session.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await session.get(User, user_id)
async def get_all_tasks(
    session: AsyncSession,
):
    result = await session.execute(select(Task))
    result = result.scalars().all()
    return [TaskSchema.model_validate(task) for task in result]
async def get_groups(session: AsyncSession) -> list[Group]:
    stmt = select(Group).order_by(Group.id)
    result: Result = await session.execute(stmt)
    groups = result.scalars().all()
    return list(groups)
