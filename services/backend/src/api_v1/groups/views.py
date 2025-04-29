from fastapi import Depends, APIRouter, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.users.dependencies import get_user_by_id, get_user_by_username
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
@router.patch('/deactivate',dependencies=[Depends(user_is_owner_of_this_group)])
async def de_active(
    group: GroupSchema = Depends(get_group_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.de_activate_group(session=session, group=group)
@router.patch('/activate',dependencies=[Depends(user_is_owner_of_this_group)])
async def active(
    group: GroupSchema = Depends(get_group_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.activate_group(session=session, group=group)
@router.patch(
    "/logo",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def update_group_logo(
    logo_url: str = Depends(upload_file),
    group: GroupSchema = Depends(get_group_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.update_group_logo(
        logo_url=logo_url,
        group=group,
        session=session,
    )
@router.get('/user_id/group')
async def get_group_for_user(
        user : User = Depends(current_active_user),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.get_group_for_user_id(session=session,user=user)
@router.get(
    '/{owner_id}/group'
)
async def get_group_where_i_owner(
        user : User = Depends(current_active_user),
        session : AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.get_my_group_for_owner(session=session,owner_id=user.id)
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
    "/{group_id}/user_id",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def add_user_in_group_by_id(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.add_user_in_group_for_id(group=group, user=user, session=session)
@router.post(
    "/{group_id}/username",
    dependencies=[Depends(user_is_owner_of_this_group)],
)
async def add_user_in_group_by_username(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(get_user_by_username),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.add_user_in_group_for_username(group=group, user=user, session=session)

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
