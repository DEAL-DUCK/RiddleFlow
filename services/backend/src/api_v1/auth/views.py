from fastapi import APIRouter
from api_v1.auth.fastapi_users import fastapi_users
from api_v1.dependencies.authentication.backend import authentication_backend
from api_v1.users.schemas import UserRead, UserCreate

router = APIRouter(tags=["Auth"])

# login and logout
router.include_router(
    router=fastapi_users.get_auth_router(authentication_backend),
)
# register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)
