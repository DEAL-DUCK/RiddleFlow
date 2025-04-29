from fastapi import Depends, HTTPException

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user, current_active_superuser
from api_v1.hackathons.schemas import HackathonBaseSchema, HackathonSchema
from core.models import User, Hackathon, Group, GroupUserAssociation, HackathonGroupAssociation, \
    HackathonUserAssociation
from core.models.group import GroupStatus


async def is_this_user_admin(
    user: User = Depends(current_active_user),
):
    if user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not admin",
    )
async def get_all_hackathons(session: AsyncSession) -> list[HackathonSchema]:
    stmt = select(Hackathon).order_by(Hackathon.id)
    result = await session.execute(stmt)
    hackathons = result.scalars().all()
    return [
        HackathonSchema(
            id=hackathon.id,
            title=hackathon.title,
            description=hackathon.description,
            start_time=hackathon.start_time,
            end_time=hackathon.end_time,
            status=hackathon.status.value,
            max_participants=hackathon.max_participants,
            current_participants=hackathon.current_participants,
            created_at=hackathon.created_at,
            updated_at=hackathon.updated_at,
            allow_teams=hackathon.allow_teams,
            logo_url=hackathon.logo_url or '',
            creator_id=hackathon.creator_id
        )
        for hackathon in hackathons
    ]
async def del_all_my_hackathon(
    session: AsyncSession,
    user_id: int
) -> dict:
    stmt = select(Hackathon).where(Hackathon.creator_id == user_id)
    result = await session.execute(stmt)
    hackathons = result.scalars().all()
    for hackathon in hackathons:
        await session.delete(hackathon)

    await session.commit()
    return {'ok': True}
async def de_active_user(session : AsyncSession,user:User):
    user.is_active = False
    await session.commit()
    return {'ok' : f'user {user.id} deactive'}
async def active_user(session : AsyncSession,user:User):
    user.is_active = True
    await session.commit()
    return {'ok' : f'user {user.id} active'}
async def BANNED(session: AsyncSession, group: Group) -> dict:
    if group.status == GroupStatus.BANNED:
        return {
            'ok': False,
            'message': f'Group {group.title} is already banned',
            'group_id': group.id
        }

    if session.in_transaction():
        await session.commit()

    result = await session.execute(
        delete(GroupUserAssociation)
        .where(GroupUserAssociation.group_id == group.id)
        .where(GroupUserAssociation.user_id != group.owner_id)
        .returning(GroupUserAssociation.user_id)
    )
    member_ids = [row[0] for row in result.all()]

    deleted_hackathons = await session.execute(
        delete(HackathonGroupAssociation)
        .where(HackathonGroupAssociation.group_id == group.id)
    )

    deleted_individual = 0
    if member_ids:
        result = await session.execute(
            delete(HackathonUserAssociation)
            .where(HackathonUserAssociation.user_id.in_(member_ids))
        )
        deleted_individual = result.rowcount

    group.status = GroupStatus.BANNED
    group.updated_at = func.now()
    group.current_members = 1

    await session.commit()

    return {
        'ok': True,
        'message': f'Group {group.title} fully banned',
        'group_id': group.id,
        'deleted_members': len(member_ids),
        'deleted_hackathon_associations': deleted_hackathons.rowcount,
        'deleted_individual_participations': deleted_individual,
        'remaining_members': 1
    }
async def UNBANNED(
        session : AsyncSession,
        group : Group
):
    group.status = GroupStatus.ACTIVE.value
    group.updated_at = func.now()
    await session.commit()

    return {
        'ok': True,
        'message': f'Group {group.title} (ID: {group.id}) has been unbanned',
    }

