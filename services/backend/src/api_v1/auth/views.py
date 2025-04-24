from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import exceptions, models, schemas
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel

from api_v1.auth.fastapi_users import fastapi_users
from api_v1.dependencies.authentication.backend import authentication_backend
from api_v1.dependencies.authentication.user_manager import get_user_manager
from api_v1.users.schemas import UserRead, UserCreate
from core.models import Profile, db_helper, User

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
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        "INVALID_ROLE": {
                            "summary": "Invalid user role",
                            "value": {
                                "detail": {
                                    "code": "INVALID_ROLE",
                                    "reason": "Role must be either PARTICIPANT or CREATOR"
                                }
                            }
                        },
                        "USERNAME_EXISTS": {
                            "summary": "Username already exists",
                            "value": {
                                "detail": {
                                    "code": "USERNAME_EXISTS",
                                    "reason": "This username is already taken"
                                }
                            }
                        },
                        "EMAIL_EXISTS": {
                            "summary": "Email already exists",
                            "value": {
                                "detail": {
                                    "code": "EMAIL_EXISTS",
                                    "reason": "User with this email already exists"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def register(
    request: Request,
    user_create: UserCreate,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    try:
        try:
            existing_user_by_email = await user_manager.get_by_email(user_create.email)
            if existing_user_by_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "EMAIL_EXISTS",
                        "reason": "User with this email already exists"
                    },
                )
        except exceptions.UserNotExists:
            pass

        existing_user_by_username = await session.execute(
            select(User).where(User.username == user_create.username)
        )
        if existing_user_by_username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "USERNAME_EXISTS",
                    "reason": "This username is already taken"
                },
            )

        user_data = user_create.model_dump()
        protected_fields = {
            'is_active': True,
            'is_superuser': False,
            'is_verified': False
        }

        created_user = await user_manager.create(
            UserCreate(**{**user_data, **protected_fields}),
            safe=True,
            request=request
        )

        profile = Profile(user_id=created_user.id)
        session.add(profile)
        await session.commit()

        return schemas.model_validate(UserRead, created_user)

    except ValueError as e:
        if "Invalid role" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_ROLE",
                    "reason": str(e)
                },
            )
        raise
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )