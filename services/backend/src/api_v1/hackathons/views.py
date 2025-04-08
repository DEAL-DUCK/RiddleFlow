from fastapi import Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from services.backend.src.api_v1.hackathons.dependencies import get_hackathon_by_id
from services.backend.src.api_v1.users.dependencies import get_user_by_id
from services.backend.src.api_v1.hackathons.schemas import (
    HackathonSchema,
    HackathonCreateSchema,
)
from services.backend.src.core.models import db_helper, User, Hackathon

router = APIRouter(tags=["Хакатоны"])


@router.get("/", response_model=list[HackathonSchema])
async def get_hackathons(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_hackathons(session=session)


@router.get("/{hackathon_id}", response_model=HackathonSchema)
async def get_hackathon(hackathon: HackathonSchema = Depends(get_hackathon_by_id)):
    return hackathon


@router.get("/{hackathon_id}/users")
async def get_users_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_users_in_hackathon(session=session, hackathon=hackathon)


@router.post("/", response_model=HackathonSchema)
async def create_hackathon(
    hackathon_in: HackathonCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_hackathon(session=session, hackathon_in=hackathon_in)


@router.post("/{hackathon_id}")
async def add_user_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.add_user_in_hackathon(
        hackathon=hackathon, user=user, session=session
    )


@router.delete("/{hackathon_id}")
async def delete_user_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.delete_user_in_hackathon(
        hackathon=hackathon, user=user, session=session
    )
