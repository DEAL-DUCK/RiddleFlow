from fastapi import APIRouter
from .hackathons.views import router as hackathons_router
from .hackathon_submissions.views import router as hackathon_submissions_router
from .hackathon_tasks.views import router as hackathon_tasks_router
from .contest_submissions.views import router as contest_submissions_router
from .contest_tasks.views import router as contest_tasks_router
from .admin.views import router as admin_router
from .contests.views import router as contests_router
from .users.views import router as users_router
from .profiles.views import router as profiles_router
from .auth.views import router as auth_router
from .groups.views import router as group_router
from .test_cases.views import router as test_router


from .jurys.views import router as jury_router
from .evaluations.views import router as jury_evaluations_router
router = APIRouter(prefix="/v1")
router.include_router(router=admin_router, prefix="/admin")
router.include_router(router=auth_router, prefix="/auth")
router.include_router(router=users_router, prefix="/users")
#router.include_router(router=group_router, prefix="/groups")
#router.include_router(router=profiles_router, prefix="/profiles")
#router.include_router(router=hackathons_router, prefix="/hackathons")
#router.include_router(
#    router=hackathon_submissions_router, prefix="/hackathon_submissions"
#)
#router.include_router(router=hackathon_tasks_router, prefix="/hackathon_tasks")
#router.include_router(router=jury_router,prefix='/jury')
#router.include_router(router=jury_evaluations_router,prefix='/jury_evaluations')
router.include_router(router=contests_router, prefix="/contests")
router.include_router(router=contest_submissions_router, prefix="/contest_submissions")
router.include_router(router=contest_tasks_router, prefix="/contest_tasks")


#router.include_router(router=group_router, prefix="/groups")
router.include_router(router=test_router, prefix="/tests")
