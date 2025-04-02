from fastapi import APIRouter
from .hackathons.views import router as hackathons_router
from services.backend.src.api_v1.auth.jwt_auth import router as jwt_auth_router
# from .olympiads.views import router as olympiads_router
from .users.views import router as users_router
from .profiles.views import router as profiles_router

router = APIRouter()
router.include_router(router=users_router, prefix="/users")
router.include_router(router=profiles_router, prefix="/profiles")
router.include_router(router=hackathons_router, prefix="/hackathons")
# router.include_router(router=olympiads_router, prefix="/olympiads")
jwt_auth_router.include_router(router=jwt_auth_router)