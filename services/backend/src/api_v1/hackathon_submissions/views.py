from typing import List
from .dependencies import user_is_participant_or_admin, check_submission_ownership
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import HackathonSubmission, User, Hackathon
from . import crud
from .schemas import HackathonSubmissionCreate
from api_v1.hackathon_submissions.schemas import (
    HackathonSubmissionRead,
    HackathonSubmissionUpdate,
)
from ..hackathons.crud import get_hackathon
from ..hackathons.dependencies import get_hackathon_by_id
from core.models.db_helper import db_helper
from ..auth.fastapi_users import current_active_user

router = APIRouter(tags=["Решения Хакатонов"])


######
@router.post("/create")
async def submissions_create(
    submission_data: HackathonSubmissionCreate,
    current_user: User = Depends(user_is_participant_or_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.create_submission(session, submission_data, current_user.id)


@router.get("/", response_model=List[HackathonSubmissionRead])
async def get_submission_endpoint(
    current_user: User = Depends(user_is_participant_or_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_my_submissions(session=session, user_id=current_user.id)


@router.get("/{submissions_id}", dependencies=[Depends(check_submission_ownership)])
async def get_submission_by_id(
    submission_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    submission = await session.get(HackathonSubmission, submission_id)
    return submission





@router.get("/task/{task_id}",dependencies=[Depends(current_active_user)])
async def get_submissions_by_user_id_and_task_id(
     task_id: int,
     user: User = Depends(current_active_user),
     session: AsyncSession = Depends(db_helper.session_getter),
 ):
     return await crud.get_submission_by_task_id_plus_user_id(
         session=session, task_id=task_id, user_id=user.id
     )


@router.delete("/{submissions_id}", dependencies=[Depends(check_submission_ownership)])
async def delete_submission(
    submission_id: int,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.delete_submission_by_id(session, submission_id)


"""@router.get("/get_all_submissions")
async def get_all_submissions(
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.all_submissions(session=session)
"""
"""@router.delete("/delete_all_submissions_any_user",)
async def delete_all_submissions_user(
    user_id: int, session: AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.delete_all_submissions_any_user(session=session, user_id=user_id)

"""


"""@router.patch(
    "/{submission_id}",
    response_model=HackathonSubmissionRead,
    dependencies=[Depends(check_submission_ownership)],
)
async def update_submission_endpoint(
    submission_id: int,
    update_data: HackathonSubmissionUpdate,
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.update_submission(
        session=session,
        submission_id=submission_id,
        update_data=update_data.model_dump(exclude_unset=True),
    )"""


@router.get("/by_hackathon/{hackathon_id}",dependencies=[Depends(current_active_user)])
async def get_submissions_by_hackathon(
        user : User = Depends(current_active_user),
         hackathon : Hackathon = Depends(get_hackathon_by_id),
         session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.get_all_submissions_current_user_in_any_hackathon(session=session, user=user, hackathon=hackathon)




# @router.get("{all_score}")
# async def get_all_score(
#     submission_id: int,
#     session: AsyncSession = Depends(db_helper.session_getter),
# ):
#     return await get_all_evaluations(session=session, submission_id=submission_id)
