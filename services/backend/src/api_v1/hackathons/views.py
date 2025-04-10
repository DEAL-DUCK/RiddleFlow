from fastapi import Depends, APIRouter, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from . import crud
from services.backend.src.api_v1.hackathons.dependencies import (
    get_hackathon_by_id,
)
from services.backend.src.api_v1.users.dependencies import get_user_by_id
from services.backend.src.api_v1.hackathons.schemas import (
    HackathonSchema,
    HackathonCreateSchema,
    HackathonUpdatePartial,
)
from services.backend.src.core.models import db_helper, User, Hackathon
from ..users.schemas import UserSchema

router = APIRouter(
    tags=["Хакатоны"],
)


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
    return await crud.get_users_in_hackathon(
        session=session,
        hackathon=hackathon,
    )


# async def get_user_in_hackathon(
#     user: User = Depends(get_user_in_hackathon_by_id),
# ):
#     return user
@router.get("/{hackathon_id}/users/{user_id}")  # тут бы еще написать response_model
async def get_user_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.get_user_in_hackathon(
        session=session,
        hackathon=hackathon,
        user_id=user.id,
    )


@router.post("/", response_model=HackathonSchema)
async def create_hackathon(
    hackathon_in: HackathonCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.create_hackathon(
        session=session,
        hackathon_in=hackathon_in,
    )


@router.post("/{hackathon_id}")
async def add_user_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.add_user_in_hackathon(
        hackathon=hackathon,
        user=user,
        session=session,
    )


@router.delete(
    "/{hackathon_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.delete_user_in_hackathon(
        hackathon=hackathon,
        user=user,
        session=session,
    )


@router.delete(
    "/{hackathon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_hackathon_admin(
    current_user: User = Depends(get_user_by_id),
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    await crud.delete_hackathon_admin(
        session=session, hackathon=hackathon, user=current_user
    )


'''@router.patch("/{hackathon_id}")
async def update_hackathon_admin(
    hackathon_update: HackathonUpdatePartial,
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    current_user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await crud.update_hackathon_admin(
        session=session,
        hackathon=hackathon,
        hackathon_update=hackathon_update,
        user=current_user,
    )
'''