from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.fastapi_users import fastapi_users
from api_v1.dependencies.authentication.backend import authentication_backend
from api_v1.dependencies.authentication.user_manager import get_user_manager
from api_v1.users.schemas import UserRead, UserCreate
from fastapi import APIRouter, Depends, HTTPException, Request, status

from fastapi_users import exceptions, models, schemas
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel

from core.models import Profile, db_helper

router = APIRouter(tags=["Auth"])

# login and logout
router.include_router(
    router=fastapi_users.get_auth_router(authentication_backend),
)
# # register
# router.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
# )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    name="register:register",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {"detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS},
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def register(
    request: Request,
    user_create: UserCreate,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        created_user = await user_manager.create(
            user_create, safe=True, request=request
        )
        profile = Profile(user_id=created_user.id)
        session.add(profile)
        await session.commit()

    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )

    return schemas.model_validate(UserRead, created_user)
