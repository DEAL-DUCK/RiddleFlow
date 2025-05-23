from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from core.models import Contest, ContestTask, ContestSubmission, Jury
from core.models.db_helper import db_helper
from api_v1.auth.fastapi_users import current_active_superuser
from api_v1.users.crud import get_users, get_user, del_user
from api_v1.users.schemas import (
    UserRead,
    UserCreate,
    UserRole,
)
from core.models import db_helper, User, Group, Hackathon
from api_v1.auth.fastapi_users import (
    current_active_user,
    current_active_superuser,
    fastapi_users,
)
from . import crud
from ..contest_submissions.schemas import ContestSubmissionRead
from ..contest_tasks.schemas import ContestTaskSchema
from ..contests.schemas import ContestSchema
from ..groups.crud import get_groups
from ..groups.dependencies import get_group_by_id
from ..hackathons.dependencies import get_hackathon_by_id
from ..hackathons.schemas import HackathonSchema
from ..hackathon_submissions.crud import (
    get_submission_by_task_id_plus_user_id,
    delete_submission_by_id,
    all_submissions,
    delete_all_submissions_any_user, get_all_submissions_current_user_in_any_hackathon,
)
from ..hackathon_submissions.dependencies import get_submission_by_id_func
from ..hackathon_tasks.crud import get_all_tasks
from ..hackathons.crud import delete_hackathon, delete_user_in_hackathon, add_user_in_hackathon
from ..jurys.depends import get_jury_by_id

router = APIRouter(tags=["АДМИН"])


@router.get("/hackathon/get", response_model=list[HackathonSchema])
async def get_hackathons_for_admin(
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(current_active_superuser),
):
    return await crud.get_all_hackathons(session=session)


@router.get(
    "/user/",
    response_model=list[UserRead],
    dependencies=[Depends(crud.is_this_user_admin)],
)
async def get_all_users(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_users(session=session)


@router.get(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(crud.is_this_user_admin)],
)
async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    user = await get_user(session=session, user_id=user_id)
    return user


@router.get(
    "/hackathon_tasks/get_all_tasks", dependencies=[Depends(crud.is_this_user_admin)]
)
async def get_all_hackathon_tasks(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await get_all_tasks(session=session)
    return result


@router.get(
    "/group/",
    dependencies=[Depends(crud.is_this_user_admin)],
)
async def get_all_groups(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_groups(session=session)


@router.get("/get_all_submissions", dependencies=[Depends(crud.is_this_user_admin)])
async def get_all_hackathon_submissions(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await all_submissions(session=session)


@router.delete(
    "/delete_all_submissions_any_user", dependencies=[Depends(crud.is_this_user_admin)]
)
async def delete_all_submissions_user_in_havkathon(
    user_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    return await delete_all_submissions_any_user(session=session, user_id=user_id)


@router.delete("/hackathon/del", dependencies=[Depends(crud.is_this_user_admin)])
async def del_hack(
    hackathon_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    return await delete_hackathon(session=session, hackathon_id=hackathon_id)
@router.post("/{hackathon_id}/users",dependencies=[Depends(current_active_superuser)])
async def add_user_in_hackathon_for_admin(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    association = await add_user_in_hackathon(
        hackathon=hackathon, user=user, session=session
    )
    return association
@router.delete('/user/delete_user_in_hack',dependencies=[Depends(current_active_superuser)])
async def delete_user_in_hackathon_for_admin(
    hackathon: Hackathon = Depends(get_hackathon_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await delete_user_in_hackathon(
        hackathon=hackathon, user=user, session=session
    )
@router.patch("/user/deactive", dependencies=[Depends(crud.is_this_user_admin)])
async def de_activate_user(
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.de_active_user(session=session, user=user)


@router.patch("/user/active", dependencies=[Depends(crud.is_this_user_admin)])
async def activate_user(
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.active_user(session=session, user=user)


@router.delete("/user/del", dependencies=[Depends(crud.is_this_user_admin)])
async def delete_user(
    user_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    return await del_user(user_id=user_id, session=session)


@router.delete("/hackathon/all_del", dependencies=[Depends(current_active_superuser)])
async def delete_all_my_hack(
    user: User = Depends(current_active_superuser),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.del_all_my_hackathon(session=session, user_id=user.id)


@router.delete("/group/ban", dependencies=[Depends(current_active_superuser)])
async def banned_group(
    session: AsyncSession = Depends(db_helper.session_getter),
    group: Group = Depends(get_group_by_id),
    user: User = Depends(current_active_superuser),
):
    return await crud.BANNED(session=session, group=group)


@router.patch("/group/unban", dependencies=[Depends(current_active_superuser)])
async def unbanned_group(
    session: AsyncSession = Depends(db_helper.session_getter),
    group: Group = Depends(get_group_by_id),
    user: User = Depends(current_active_superuser),
):
    return await crud.UNBANNED(session=session, group=group)


@router.get("/task/{task_id}", dependencies=[Depends(current_active_superuser)])
async def get_submissions_hackathon_by_user_id_and_task_id(
        task_id: int,
        user: User = Depends(get_user_by_id),
        session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_submission_by_task_id_plus_user_id(
        session=session, task_id=task_id, user_id=user.id
    )


@router.get("/by_hackathon/{hackathon_id}", dependencies=[Depends(current_active_superuser)])
async def get_submissions_by_hackathon(
        user: User = Depends(get_user_by_id),
        hackathon: Hackathon = Depends(get_hackathon_by_id),
        session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_all_submissions_current_user_in_any_hackathon(session=session, user=user, hackathon=hackathon)

"""@router.delete(
    "/groups/delete-all",
    dependencies=[Depends(current_active_superuser)],
    summary=f"СНЕСЕНА ФУНКЦИЯ",
)
async def delete_all_groups_route(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return f"СНЕСЕНА ФУНКЦИЯ"


@router.delete(
    "/groups/{group_id}",
    dependencies=[Depends(current_active_user)],
    summary=f"СНЕСЕНА ФУНКЦИЯ",
)
async def delete_group_route(
    group_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
    current_user: User = Depends(current_active_user),
):
    group = await session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user.id != group.owner_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner or admin can delete group",
        )

    return f"СНЕСЕНА ФУНКЦИЯ"""



@router.get("/contests/", response_model=List[ContestSchema])
async def admin_get_all_contests(
    session: AsyncSession = Depends(db_helper.session_getter),
    _: bool = Depends(current_active_superuser),
):
    """Получение всех контестов (только админ)"""
    result = await session.execute(select(Contest))
    contests = result.scalars().all()
    return [ContestSchema.model_validate(contest) for contest in contests]

@router.get("/contests/tasks/", response_model=List[ContestTaskSchema])
async def admin_get_all_contest_tasks(
    session: AsyncSession = Depends(db_helper.session_getter),
    _: bool = Depends(current_active_superuser),
):
    """Получение всех задач всех контестов (только админ)"""
    result = await session.execute(select(ContestTask))
    tasks = result.scalars().all()
    return [ContestTaskSchema.model_validate(task) for task in tasks]

@router.get("/contests/submissions/", response_model=List[ContestSubmissionRead])
async def admin_get_all_contest_submissions(
    session: AsyncSession = Depends(db_helper.session_getter),
    _: bool = Depends(current_active_superuser),
):
    """Получение всех решений контестов (только админ)"""
    result = await session.execute(select(ContestSubmission))
    submissions = result.scalars().all()
    return [ContestSubmissionRead.model_validate(sub) for sub in submissions]
@router.delete("/contest/all_del", dependencies=[Depends(current_active_superuser)])
async def delete_all_my_hack(
    user: User = Depends(current_active_superuser),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.del_all_my_contest(session=session, user_id=user.id)