from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from api_v1.auth.fastapi_users import current_active_user, current_active_superuser
from api_v1.hackathons.dependencies import (
    get_hackathon_by_id,
    user_is_creator_of_this_hackathon,
)
from api_v1.users.dependencies import (
    get_user_by_id,
    user_is_creator,
    user_is_participant,
)
from api_v1.hackathons.schemas import (
    HackathonSchema,
    HackathonCreateSchema,
    HackathonUpdatePartial,
)
from core.models import db_helper, User, Hackathon, Group
from ..groups.dependencies import (
    get_group_by_id,
    user_is_owner_of_this_group,
    user_is_owner_of_this_group_or_hackathon_creator,
)

router = APIRouter(tags=["Хакатоны"])


@router.get("/", response_model=list[HackathonSchema])
async def get_hackathons(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_hackathons(session=session)


@router.get(
    "/{hackathon_id}",
    response_model=HackathonSchema,
    dependencies=[Depends(current_active_user)],
)
async def get_hackathon(hackathon: HackathonSchema = Depends(get_hackathon_by_id)):
    return hackathon


@router.post(
    "/",
    response_model=HackathonSchema,
)
async def create_hackathon(
    hackathon_in: HackathonCreateSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator),
):
    return await crud.create_hackathon(
        session=session, hackathon_in=hackathon_in, user_id=user.id
    )


@router.patch("/")
async def update_hackathon(
    hackathon_in: HackathonUpdatePartial,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator_of_this_hackathon),
    hackathon: Hackathon = Depends(get_hackathon_by_id),
):
    return await crud.update_hackathon(
        session=session,
        hackathon_in=hackathon_in,
        hackathon=hackathon,
    )


@router.get(
    "/{hackathon_id}/users",
    dependencies=[Depends(user_is_creator_of_this_hackathon)],
)
async def get_users_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_users_in_hackathon(session=session, hackathon=hackathon)


@router.post("/{hackathon_id}/users")
async def add_user_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(user_is_participant),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    association = await crud.add_user_in_hackathon(
        hackathon=hackathon, user=user, session=session
    )
    return association


@router.delete("/{hackathon_id}/users",
               dependencies=[Depends(user_is_creator_of_this_hackathon)])
async def delete_user_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(user_is_participant),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.delete_user_in_hackathon(
        hackathon=hackathon, user=user, session=session
    )


@router.get(
    "/{hackathon_id}/groups",
    dependencies=[Depends(user_is_creator_of_this_hackathon)],
)
async def get_groups_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_groups_in_hackathon(session=session, hackathon=hackathon)


@router.post(
    "/{hackathon_id}/groups",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def add_group_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    group: Group = Depends(get_group_by_id),
    user: User = Depends(user_is_owner_of_this_group),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.add_group_in_hackathon(
        hackathon=hackathon, group=group, session=session
    )


@router.delete(
    "/{hackathon_id}/groups",
    dependencies=[Depends(user_is_owner_of_this_group_or_hackathon_creator)],
)
async def delete_group_in_hackathon(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    group: Group = Depends(get_group_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.delete_group_in_hackathon(
        hackathon=hackathon, group=group, session=session
    )


#
# @router.get("/{hackathon_id}/jury")
# async def get_hackathon_jury(
#     hackathon_id: int,
#     session: AsyncSession = Depends(db_helper.scoped_session_dependency),
# ):
#     return await crud.get_all_jury_in_hackathon(
#         session=session,
#         hackathon_id=hackathon_id,
#     )
