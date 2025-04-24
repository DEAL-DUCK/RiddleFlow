from fastapi import APIRouter
from .hackathons.views import router as hackathons_router
from .submissions.views import router as submissions_router
from .tasks.views import router as tasks_router
from .admin.views import router as admin_router
#from .olympiads.views import router as olympiads_router
from .users.views import router as users_router
from .profiles.views import router as profiles_router
from .auth.views import router as auth_router
from .groups.views import router as group_router


router = APIRouter(prefix="/v1")
router.include_router(router=admin_router,prefix='/admin')
router.include_router(router=auth_router, prefix="/auth")
router.include_router(router=users_router, prefix="/users")
router.include_router(router=profiles_router, prefix="/profiles")
router.include_router(router=hackathons_router, prefix="/hackathons")
# router.include_router(router=olympiads_router, prefix="/olympiads")

router.include_router(router=submissions_router, prefix="/submissions")
router.include_router(router=tasks_router, prefix="/tasks")
router.include_router(router=group_router, prefix="/groups")
