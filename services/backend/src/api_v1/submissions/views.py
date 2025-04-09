from http.client import HTTPException
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .crud import *
from api_v1.submissions.schemas import SubmissionRead, SubmissionCreate
from core.models import Submission, db_helper

router = APIRouter(tags=["Решения"])
@router.post(
    "/{submission_create}",
    response_model=SubmissionRead,
)
async def create_submission_endpoint(
    submission_data: SubmissionCreate,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await create_submission(session, submission_data)

@router.get('/users_submissions',response_model=List[SubmissionRead])
async def get_submission_endpoint(
    user_id : int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    return await get_user_submissions(session, user_id)
@router.get('/submission_by_id',response_model=SubmissionRead)
async def get_submission_by_id(
        submission_id : int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await get_submission_by_id_func(session, submission_id)
@router.get('/submissions_by_user_id+submissions_id',response_model=SubmissionRead)
async def get_submissions_by_user_id_and_submission_id(
        user_id : int,
        submission_id : int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await get_submission_by_id_plus_user_id(session, submission_id, user_id)
@router.delete('/delete_submission')
async def delete_submission(
        submission_id : int,
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await delete_submission_by_id(session, submission_id)
@router.get('/get_all_submissions')
async def get_all_submissions(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await all_submissions(session=session)
@router.delete('/delete_all_submissions_any_user')
async def delete_all_submissions_user(
        user_id : int,
        session : AsyncSession = Depends(db_helper.scoped_session_dependency)
):
    return await delete_all_submissions_any_user(session=session, user_id=user_id)