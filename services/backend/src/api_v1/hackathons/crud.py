from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from services.backend.src.api_v1.hackathons.schemas import (
    HackathonCreateSchema,
)
from services.backend.src.core.models import Hackathon, User


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


async def add_user_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
    user: User,
):
    hackathon = await session.scalar(
        select(Hackathon)
        .where(Hackathon.id == hackathon.id)
        .options(selectinload(Hackathon.users)),
    )
    if user not in hackathon.users:
        hackathon.users.append(user)
        await session.commit()
        return hackathon.users
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"User {user.id} is already participating in this hackathon",
    )


async def delete_user_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
    user: User,
):
    hackathon = await session.scalar(
        select(Hackathon)
        .where(Hackathon.id == hackathon.id)
        .options(selectinload(Hackathon.users)),
    )
    if user in hackathon.users:
        hackathon.users.remove(user)
        await session.commit()
        return hackathon.users
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {user.id} is not participating in this hackathon",
    )


async def get_users_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
):
    hackathon = await session.scalar(
        select(Hackathon)
        .where(Hackathon.id == hackathon.id)
        .options(selectinload(Hackathon.users)),
    )
    return hackathon.users
