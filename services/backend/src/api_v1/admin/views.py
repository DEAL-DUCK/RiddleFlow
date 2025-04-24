from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.users.crud import get_users, get_user
from api_v1.users.schemas import (
    UserSchema,
    UserRead,
    UserUpdate,
)
from core.models import db_helper, User
from api_v1.auth.fastapi_users import (
    current_active_user,
    current_active_superuser,
    fastapi_users,
)
from .crud import is_this_user_admin,get_all_hackathons
from ..groups.crud import get_groups
from ..hackathons.schemas import HackathonSchema
from ..submissions.crud import get_submission_by_id_func, get_submission_by_task_id_plus_user_id, \
    delete_submission_by_id, all_submissions, delete_all_submissions_any_user
from ..submissions.schemas import SubmissionRead
from ..tasks.crud import get_all_tasks
from ..hackathons.crud import delete_hackathon

router = APIRouter(tags=["АДМИН"])
@router.get("/hackathon/get", response_model=list[HackathonSchema])
async def get_hackathons_for_admin(
    session: AsyncSession = Depends(db_helper.session_getter),
    user : User = Depends(current_active_superuser)
):
    return await get_all_hackathons(session=session)
@router.get(
    "/user/",
    response_model=list[UserSchema],
    dependencies=[Depends(is_this_user_admin)],
)
async def get_all_users(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_users(session=session)
@router.get(
    '/{id}',
    response_model=UserSchema,
    dependencies=[Depends(is_this_user_admin)],
)
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(db_helper.session_getter)):
    user = await get_user(session=session, user_id=user_id)
    return user

@router.get("/tasks/get_all_tasks",dependencies=[Depends(is_this_user_admin)])
async def get_all_tasks_(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    result = await get_all_tasks(session=session)
    return result

@router.get(
    "/group/",
    dependencies=[Depends(is_this_user_admin)],
)
async def get_all_groups(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await get_groups(session=session)
@router.get("/get_all_submissions",dependencies=[Depends(is_this_user_admin)])
async def get_all_submissions(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await all_submissions(session=session)
@router.delete("/delete_all_submissions_any_user",dependencies=[Depends(is_this_user_admin)])
async def delete_all_submissions_user(
    user_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    return await delete_all_submissions_any_user(session=session, user_id=user_id)
@router.delete('/hackathon/del',dependencies=[Depends(is_this_user_admin)])
async def del_hack(
        hackathon_id : int , session: AsyncSession = Depends(db_helper.session_getter)
):
    return await delete_hackathon(session=session,hackathon_id=hackathon_id)