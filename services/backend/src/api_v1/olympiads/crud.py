from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.olympiads.schemas import OlympiadCreateSchema

from core.models import Olympiad


async def get_olympiads(session: AsyncSession) -> list[Olympiad]:
    stmt = select(Olympiad).order_by(Olympiad.id)
    result: Result = await session.execute(stmt)
    olympiads = result.scalars().all()
    return list(olympiads)


async def get_olympiad(session: AsyncSession, olympiad_id: int) -> Olympiad | None:
    return await session.get(Olympiad, olympiad_id)


async def create_olympiad(
    session: AsyncSession, olympiad_in: OlympiadCreateSchema
) -> Olympiad:
    olympiad = Olympiad(**olympiad_in.model_dump())
    session.add(olympiad)
    await session.commit()
    return olympiad
