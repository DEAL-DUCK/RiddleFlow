from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.hackathons.schemas import (
    HackathonCreateSchema,
)
from core.models import Hackathon, User, HackathonUserAssociation
from core.models.hackathon_user_association import (
    ParticipationStatus,
)


async def get_hackathons(session: AsyncSession) -> list[Hackathon]:
    stmt = select(Hackathon).order_by(Hackathon.id)
    result: Result = await session.execute(stmt)
    hackathons = result.scalars().all()
    return list(hackathons)


async def get_hackathon(session: AsyncSession, hackathon_id: int) -> Hackathon | None:
    return await session.get(Hackathon, hackathon_id)


async def create_hackathon(
    session: AsyncSession,
    hackathon_in: HackathonCreateSchema,
) -> Hackathon:
    hackathon = Hackathon(**hackathon_in.model_dump())
    session.add(hackathon)
    await session.commit()
    return hackathon


async def add_user_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
    user: User,
):
    existing_association = await session.scalar(
        select(HackathonUserAssociation)
        .where(HackathonUserAssociation.hackathon_id == hackathon.id)
        .where(HackathonUserAssociation.user_id == user.id)
    )

    if existing_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User  {user.id} is already participating in this hackathon",
        )

    # Создаем новую ассоциацию
    association = HackathonUserAssociation(
        hackathon_id=hackathon.id,
        user_id=user.id,
        user_status=ParticipationStatus.REGISTERED,
    )

    session.add(association)
    await session.commit()
    return association


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
        await session.delete(association)
        await session.commit()
        return association
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User  {user.id} is not participating in this hackathon",
    )


async def get_users_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
):
    result = await session.execute(
        select(HackathonUserAssociation)
        .options(selectinload(HackathonUserAssociation.user))
        .where(HackathonUserAssociation.hackathon_id == hackathon.id)
    )
    associations = result.scalars().all()
    return [
        {
            "user_info": {
                "id": assoc.user.id,
                "username": assoc.user.username,
                "email": assoc.user.email,
            },
            "user_details": {
                "status": assoc.user_status.value,
                "registration_date": assoc.registration_date.isoformat(),
            },
        }
        for assoc in associations
    ]


async def get_groups_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
):
    result = await session.execute(
        select(HackathonGroupAssociation)
        .options(selectinload(HackathonGroupAssociation.group))
        .where(HackathonGroupAssociation.hackathon_id == hackathon.id)
    )
    associations = result.scalars().all()
    return [
        {
            "group_info": {
                "id": assoc.group.id,
                "title": assoc.group.title,
                "owner_id": assoc.group.owner_id,
                "max_members": assoc.group.max_members,
                "current_members": assoc.group.current_members,
            },
            "group_details": {
                "group_status": assoc.group_status,
                "registration_date": assoc.registration_date,
            },
        }
        for assoc in associations
    ]


async def add_group_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
    group: Group,
):
    if hackathon.status != "PLANNED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"acceptance of applications to the hackathon {hackathon.id} is completed",
        )
    existing_association = await session.scalar(
        select(HackathonGroupAssociation)
        .where(HackathonGroupAssociation.hackathon_id == hackathon.id)
        .where(HackathonGroupAssociation.group_id == group.id)
    )

    if existing_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Group {group.id} is already participating in this hackathon",
        )
    if (
        hackathon.max_participants
        <= hackathon.current_participants + group.current_members
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No available spots in the hackathon.",
        )
    association = HackathonGroupAssociation(
        hackathon_id=hackathon.id,
        group_id=group.id,
        group_status=TeamStatus.REGISTERED,
    )

    hackathon.current_participants += group.current_members
    session.add(association)
    await session.commit()
    result = await session.execute(
        select(GroupUserAssociation)
        .options(selectinload(GroupUserAssociation.user))
        .where(GroupUserAssociation.group_id == group.id)
    )
    users_assoc = result.scalars().all()
    for assoc in users_assoc:
        await add_user_in_hackathon(
            session=session,
            hackathon=hackathon,
            user=assoc.user,
        )
    return association


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


# async def get_user_in_hackathon(
#     session: AsyncSession,
#     hackathon: Hackathon,
#     user_id: int,
# ):
#     # тут идет запрос в бдшку по айди хакатона и айди юзера(скопипастил, проверь чтобы верно было)
#     association = await session.scalar(
#         select(HackathonUserAssociation)
#         .where(HackathonUserAssociation.hackathon_id == hackathon.id)
#         .where(HackathonUserAssociation.user_id == user_id)
#     )
#
#     if association:
#         return {
#             "user": {
#                 "id": association.user.id,
#                 "username": association.user.username,
#                 "email": association.user.email,
#                 "status": association.user_status,
#                 "role": association.user_role,
#                 "created_hackathons": association.user.created_hackathons,
#             },
#         }
#
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"User  {user_id} is not participating in this hackathon",
#     )


# async def get_all_jury_in_hackathon(
#         session: AsyncSession,
#         hackathon_id: int,
# ):
#     if not await get_hackathon(session=session,hackathon_id=hackathon_id): return any_not('hackathon_id')
#     result = await session.execute(
#         select(JuryHackathonAssociation)
#         .where(JuryHackathonAssociation.hackathon_id == hackathon_id)
#     )
#     return list(result.scalars().all())
#
