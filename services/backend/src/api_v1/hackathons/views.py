from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from services.backend.src.api_v1.hackathons.dependencies import get_hackathon_by_id
from services.backend.src.api_v1.hackathons.schemas import (
    HackathonSchema,
    HackathonCreateSchema,
)
from services.backend.src.core.models import db_helper

router = APIRouter(tags=["Хакатоны"])


@router.get("/", response_model=list[HackathonSchema])
async def get_hackathons(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_hackathons(session=session)


@router.get("/{hackathon_id}", response_model=HackathonSchema)
async def get_hackathon(hackathon: HackathonSchema = Depends(get_hackathon_by_id)):
    return hackathon


@router.post("/", response_model=HackathonSchema)
async def create_hackathon(
    hackathon_in: HackathonCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_hackathon(session=session, hackathon_in=hackathon_in)
