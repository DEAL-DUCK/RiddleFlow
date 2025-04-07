from fastapi import APIRouter
from api_v1.auth.fastapi_users import fastapi_users
from api_v1.dependencies.authentication.backend import authentication_backend

router = APIRouter(tags=["Auth"])

router.include_router(
    router=fastapi_users.get_auth_router(authentication_backend),
)
