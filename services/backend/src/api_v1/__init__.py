from fastapi import APIRouter
from .hackathons.views import router as hackathons_router
from .Task.views import router as tasks_router
# from .olympiads.views import router as olympiads_router
from .users.views import router as users_router
from .profiles.views import router as profiles_router
from .submissions.views import router as submissions_router
from .jurys.views import router as jury_router
from .evaluations.views import router as evaluations_router
router = APIRouter()
router.include_router(router=users_router, prefix="/users")
router.include_router(router=profiles_router, prefix="/profiles")
router.include_router(router=hackathons_router, prefix="/hackathons")
# router.include_router(router=olympiads_router, prefix="/olympiads")
router.include_router(router=tasks_router, prefix="/tasks")
router.include_router(router=submissions_router, prefix="/submissions")
router.include_router(router=jury_router, prefix="/jury")
router.include_router(router=evaluations_router, prefix="/evaluations")
