from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from services.backend.src.api_v1.olympiads.dependencies import get_olympiad_by_id
from services.backend.src.api_v1.olympiads.schemas import (
    OlympiadSchema,
    OlympiadCreateSchema,
)
from services.backend.src.core.models import db_helper

router = APIRouter(tags=["Олимпиады"])


@router.get("/", response_model=list[OlympiadSchema])
async def get_olympiads(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_olympiads(session=session)


@router.get("/{olympiad_id}", response_model=OlympiadSchema)
async def get_olympiad(olympiad: OlympiadSchema = Depends(get_olympiad_by_id)):
    return olympiad


@router.post("/", response_model=OlympiadSchema)
async def create_olympiad(
    olympiad_in: OlympiadCreateSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.create_olympiad(session=session, olympiad_in=olympiad_in)
