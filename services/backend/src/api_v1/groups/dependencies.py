from typing import Annotated

from fastapi import Path, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import os
from core.config import s3_client, settings
from api_v1.auth.fastapi_users import current_active_user
from api_v1.groups.crud import get_group
from api_v1.hackathons.dependencies import get_hackathon_by_id
from api_v1.users.dependencies import user_is_participant
from core.models import db_helper, Group, User, Hackathon


async def get_group_by_id(
    group_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Group:
    group = await get_group(session=session, group_id=group_id)
    if group is not None:
        return group
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Group {group_id} if not found",
    )


async def user_is_owner_of_this_group(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(user_is_participant),
):
    if group.owner_id == user.id:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not owner of group",
    )


async def user_is_owner_of_this_group_or_hackathon_creator(
    group: Group = Depends(get_group_by_id),
    user: User = Depends(current_active_user),
    hackathon: Hackathon = Depends(get_hackathon_by_id),
):
    if group.owner_id == user.id or user.id == hackathon.creator_id:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not owner of group",
    )


from fastapi import HTTPException, status
import imghdr  # Для проверки типа изображения
from typing import Tuple

ALLOWED_IMAGE_TYPES = {'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024

async def upload_file(
    upload_file: UploadFile = File(...),
) -> str:
    # Проверка размера файла
    if upload_file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE//(1024*1024)}MB"
        )

    filename = upload_file.filename
    file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if file_ext not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    file_path = f"src/tmp/{filename}"
    with open(file_path, "wb") as f:
        f.write(await upload_file.read())
    file_type = imghdr.what(file_path)
    if file_type not in ALLOWED_IMAGE_TYPES:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не является изображением или имеет недопустимый формат"
        )
    try:
        await s3_client.upload_file(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return f"{settings.s3.domain_url}/{filename}"
# TODO: сделать функцию удаления файла с s3 хранилища по его url
# async def delete_file(
#     file_url: str,
# ):
#     await
