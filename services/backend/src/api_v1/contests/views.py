from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from . import crud
from api_v1.auth.fastapi_users import current_active_user, current_active_superuser
from api_v1.contests.dependencies import (
    get_contest_by_id,
    user_is_creator_of_this_contest, get_inactive_contest,
)
from api_v1.users.dependencies import (
    get_user_by_id,
    user_is_creator,
    user_is_participant,
)
from api_v1.contests.schemas import (
    ContestSchema,
    ContestCreateSchema,
    ContestUpdatePartial,
)
from core.models import db_helper, User, Contest, Group
from ..groups.dependencies import (
    get_group_by_id,
    user_is_owner_of_this_group,
    user_is_owner_of_this_group_or_contest_creator,
    upload_file,
)

router = APIRouter(tags=["Контесты"])

@router.patch('/archive/in',dependencies=[Depends(user_is_creator_of_this_contest),])
async def archived(contest : Contest = Depends(get_inactive_contest),
        session: AsyncSession = Depends(db_helper.session_getter)):
    return await crud.archive(session=session,contest=contest)
@router.patch('/archive/un',dependencies=[Depends(user_is_creator_of_this_contest)])
async def unarchived(contest : Contest = Depends(get_contest_by_id),
        session: AsyncSession = Depends(db_helper.session_getter)):
    return await crud.unarchive(session=session,contest=contest)

@router.get("/", response_model=list[ContestSchema])
async def get_contests(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_contests(session=session)


@router.get(
    "/{contest_id}",
    response_model=ContestSchema,
    dependencies=[Depends(current_active_user)],
)
# ПУСТЬ ЭТО БУДЕТ ДЛЯ ВСЕХ ДАЖЕ НЕ ЗАРЕГАННЫХ
async def get_contest(
    contest: ContestSchema = Depends(get_contest_by_id),
):  # УБРАЛ ПЕРЕВОД В СХЕМУ ContestSchema для celery
    return contest


@router.get("{/contest_id}", response_model=ContestSchema, dependencies=[])
async def get_contest_by_name(
    tittle: str, session: AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.get_contest_by_tittle(contest_title=tittle, session=session)


@router.get(
    "/me/partial/",
    response_model=List[ContestSchema],
    summary="contest when i participant",
)
async def get_my_contests_when_i_participant(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_contests_for_user(session=session, user_id=current_user.id)


@router.get(
    "/me/created/",
    response_model=List[ContestSchema],
    dependencies=[Depends(user_is_creator)],
)
async def get_hack_when_i_creator(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_contest_for_creator(session=session, user_id=current_user.id)


@router.post(
    "/",
    response_model=ContestSchema,
    summary="""PLANNED
    ACTIVE 
    COMPLETED
    CANCELED """,
)
async def create_contest(
    contest_in: ContestCreateSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator),
):
    return await crud.create_contest(
        session=session, contest_in=contest_in, user_id=user.id
    )


@router.patch("/", response_model=ContestSchema)
async def update_contest(
    contest_in: ContestUpdatePartial,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator_of_this_contest),
    contest: Contest = Depends(get_inactive_contest),
):
    return await crud.update_contest(
        session=session, contest_in=contest_in, contest=contest, user=user
    )


@router.patch(
    "/logo",
    dependencies=[Depends(user_is_creator_of_this_contest)],
)
async def update_contest_logo(
    logo_url: str = Depends(upload_file),
    contest: ContestSchema = Depends(get_contest_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.update_contest_logo(
        logo_url=logo_url,
        contest=contest,
        session=session,
    )


@router.patch("/contest_id}/activate", summary="activate contest")
async def force_activate_hack(
    contest: Contest = Depends(get_inactive_contest),
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator_of_this_contest),
):
    return await crud.activate_contest(session=session, contest=contest)


@router.patch("/{contest_id}/deactivate", summary="deactivate contest")
async def cancel_contest(
    contest: Contest = Depends(get_contest_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator_of_this_contest),
):
    return await crud.cancel_contest(session=session, contest=contest)


@router.patch("/{contest_id}/max_participant")
async def change_max_participant(
    new_max_users: int,
    contest: Contest = Depends(get_inactive_contest),
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_creator_of_this_contest),
):
    return await crud.patch_max_users_in_contest(
        session=session, contest=contest, max_participants=new_max_users, user=user
    )


@router.get(
    "/{contest_id}/users",
    dependencies=[Depends(user_is_creator_of_this_contest)],
)
async def get_users_in_contest(
    contest: Contest = Depends(get_contest_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_users_in_contest(session=session, contest=contest)


@router.post("/{contest_id}/users")
async def add_user_in_contest(
    contest: Contest = Depends(get_contest_by_id),
    user: User = Depends(user_is_participant),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    association = await crud.add_user_in_contest(
        contest=contest, user=user, session=session
    )
    return association


@router.delete(
    "/{contest_id}/users", dependencies=[Depends(user_is_creator_of_this_contest)]
)
async def delete_user_in_contest(
    contest: Contest = Depends(get_contest_by_id),
    user: User = Depends(user_is_participant),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.delete_user_in_contest(
        contest=contest, user=user, session=session
    )


@router.get(
    "/{contest_id}/groups",
    dependencies=[Depends(user_is_creator_of_this_contest)],
)
async def get_groups_in_contest(
    contest: Contest = Depends(get_contest_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_groups_in_contest(session=session, contest=contest)


@router.post(
    "/{contest_id}/groups",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def add_group_in_contest(
    contest: Contest = Depends(get_contest_by_id),
    group: Group = Depends(get_group_by_id),
    user: User = Depends(user_is_owner_of_this_group),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.add_group_in_contest(
        contest=contest, group=group, session=session
    )


@router.delete(
    "/{contest_id}/groups",
    dependencies=[Depends(user_is_owner_of_this_group_or_contest_creator)],
)
async def delete_group_in_contests(
    contest: Contest = Depends(get_contest_by_id),
    group: Group = Depends(get_group_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.delete_group_in_contest(
        contest=contest, group=group, session=session
    )


#
# @router.get("/{contest_id}/jury")
# async def get_contest_jury(
#     contest_id: int,
#     session: AsyncSession = Depends(db_helper.scoped_session_dependency),
# ):
#     return await crud.get_all_jury_in_contest(
#         session=session,
#         contest_id=contest_id,
#     )
