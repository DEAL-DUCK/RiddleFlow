from fastapi import Depends, APIRouter, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.users.dependencies import get_user_by_id
from .dependencies import get_group_by_id, user_is_owner_of_this_group, upload_file
from . import crud

from core.models import db_helper, Group, User
from .schemas import GroupCreateSchema, GroupUpdateSchema, GroupSchema
from api_v1.auth.fastapi_users import current_active_superuser, current_active_user
from api_v1.users.dependencies import user_is_participant


router = APIRouter(tags=["Группы"])

"""@router.get(
    "/",
    dependencies=[Depends(current_active_superuser)],
)
async def get_groups(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_groups(session=session)
"""


@router.get(
    "/{group_id}",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def get_group(
    group: GroupSchema = Depends(get_group_by_id),
):
    return group


# # TODO: ПЕРЕПИШИ ДЛЯ ХАКАТОНОВ, создание+обновка. УДАЛЯЙ СОХРАНЁННЫЕ ФАЙЛЫ. Ссылку добавь в бд.
# @router.post("/upload_test")


@router.post("/")
async def create_group(
    group_in: GroupCreateSchema,
    session: AsyncSession = Depends(db_helper.session_getter),
    user: User = Depends(user_is_participant),
):
    return await crud.create_group(
        group_in=group_in,
        session=session,
        user_id=user.id,
    )


@router.patch(
    "/",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def update_group(
    group_in: GroupUpdateSchema,
    group: GroupSchema = Depends(get_group_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.update_group(
        group_in=group_in,
        group=group,
        session=session,
    )


@router.get(
    "/{group_id}/users",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def get_users_in_group(
    group: Group = Depends(get_group_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_users_in_group(session=session, group=group)


@router.post(
    "/{group_id}/users",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def add_user_in_group(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.add_user_in_group(group=group, user=user, session=session)


@router.delete(
    "/{group_id}/users",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def delete_user_in_group(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.delete_user_in_group(group=group, user=user, session=session)
