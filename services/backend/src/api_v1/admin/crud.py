from fastapi import Depends, HTTPException
from starlette import status

from api_v1.auth.fastapi_users import current_active_user
from core.models import User


async def is_this_user_admin(
    user: User = Depends(current_active_user),
):
    if user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not admin",
    )
