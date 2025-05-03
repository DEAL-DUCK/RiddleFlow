from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from . import schemas
from core.models import db_helper, User, Hackathon, Jury
from . import crud
from .depends import get_jury_by_id, is_this_user_jury_this_hackathon
from ..auth.fastapi_users import current_active_user, current_active_superuser
from ..evaluations.depends import get_current_jury
from ..hackathons.dependencies import get_hackathon_by_id, user_is_creator_of_this_hackathon
from ..users.dependencies import get_user_by_id

router = APIRouter(tags=["Жюри"])



@router.post(
    "/hackathon/add",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(user_is_creator_of_this_hackathon)]
)
async def add_jury_member_to_hackathon_endpoint(
    user : User = Depends(get_user_by_id),
    hackathon : Hackathon = Depends(get_hackathon_by_id),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    return await crud.add_jury_to_hackathon(hackathon=hackathon,user=user,session=session)

@router.delete(
    '/hackathon/del',
    dependencies=[Depends(user_is_creator_of_this_hackathon)]
)
async def del_jury_from_hackathon(
        jury : Jury = Depends(is_this_user_jury_this_hackathon),
        hackathon: Hackathon = Depends(get_hackathon_by_id),
        session: AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.remove_jury_from_hackathon(
        session=session,
        jury=jury,
        hackathon=hackathon
    )
@router.get(
    '/get_all_hackathons_where_this_jury_work',
    dependencies=[Depends(current_active_user)],
)
async def get_all_hackathons_where_this_jury_work(
jury:Jury=Depends(get_jury_by_id),
session: AsyncSession = Depends(db_helper.session_getter)):
    return await crud.get_hackathons_judged_by_jury(
        session=session,
        jury=jury
    )

@router.get(
    '/get_all_hackathons_where_this_jury_work/for_hackathon_id',
    dependencies=[Depends(user_is_creator_of_this_hackathon)]
)
async def get_my_evalution_by_hackathon(
        session : AsyncSession = Depends(db_helper.session_getter),
        hackathon : Hackathon = Depends(get_hackathon_by_id),
        jury : Jury = Depends(get_current_jury)
):
    return await crud.get_jury_evaluations_with_this_hackathon(
        session=session, jury=jury, hackathon = hackathon
    )



@router.get("/{jury_id}/evaluations",
            dependencies=[Depends(current_active_superuser)]
            ,summary='ADMIN')
async def get_jury_evaluations_for_admin(
    jury : Jury = Depends(get_jury_by_id),
    session: AsyncSession = Depends(db_helper.session_getter)
):
    return await crud.get_jury_evaluations_with_details(session=session, jury=jury)



@router.get('/{jury_id}',dependencies=[Depends(current_active_superuser)])
async def get_jury_for_admin(
        jury_id : int,
session: AsyncSession = Depends(db_helper.session_getter)
):
    return await get_jury_by_id(session=session,jury_id=jury_id)


