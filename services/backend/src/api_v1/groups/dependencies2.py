from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.models import Group, Hackathon, GroupUserAssociation, HackathonGroupAssociation, User, \
    HackathonUserAssociation


async def delete_group_in_hackathon(
        session: AsyncSession,
        hackathon: Hackathon,
        group: Group,
):
    association = await session.scalar(
        select(HackathonGroupAssociation)
        .where(HackathonGroupAssociation.hackathon_id == hackathon.id)
        .where(HackathonGroupAssociation.group_id == group.id)
    )

    if association:
        await session.delete(association)
        await session.commit()
        result = await session.execute(
            select(GroupUserAssociation)
            .options(selectinload(GroupUserAssociation.user))
            .where(GroupUserAssociation.group_id == group.id)
        )
        users_assoc = result.scalars().all()
        for assoc in users_assoc:
            await delete_user_in_hackathon(
                session=session,
                hackathon=hackathon,
                user=assoc.user,
            )
        hackathon.current_participants -= group.current_members
        return {"delete": True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Group {group.id} is not participating in this hackathon",
    )
async def del_group_in_hack(
        session : AsyncSession,
        group : Group,
        hackathon : Hackathon
):
    await delete_group_in_hackathon(session=session,hackathon=hackathon,group=group)
async def delete_user_in_hackathon(
        session: AsyncSession,
        hackathon: Hackathon,
        user: User,
):
    # Находим ассоциацию между пользователем и хакатоном
    association = await session.scalar(
        select(HackathonUserAssociation)
        .where(HackathonUserAssociation.hackathon_id == hackathon.id)
        .where(HackathonUserAssociation.user_id == user.id)
    )

    if association:
        hackathon.current_participants -= 1
        await session.delete(association)
        await session.commit()
        return {"delete": True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User  {user.id} is not participating in this hackathon",
    )