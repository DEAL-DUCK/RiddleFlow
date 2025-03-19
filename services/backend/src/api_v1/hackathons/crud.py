from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from services.backend.src.api_v1.hackathons.schemas import HackathonCreateSchema
from services.backend.src.core.models import Hackathon


async def get_hackathons(session: AsyncSession) -> list[Hackathon]:
    stmt = select(Hackathon).order_by(Hackathon.id)
    result: Result = await session.execute(stmt)
    hackathons = result.scalars().all()
    return list(hackathons)


async def get_hackathon(session: AsyncSession, hackathon_id: int) -> Hackathon | None:
    return await session.get(Hackathon, hackathon_id)


async def create_hackathon(
    session: AsyncSession, hackathon_in: HackathonCreateSchema
) -> Hackathon:
    hackathon = Hackathon(**hackathon_in.model_dump())
    session.add(hackathon)
    await session.commit()
    return hackathon
