import logging

from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import json
from api_v1.hackathons.schemas import (
    HackathonCreateSchema,
    HackathonUpdatePartial,
    HackathonSchema,
    HackathonBaseSchema,
)
from core.config import redis_client
from core.models import (
    Hackathon,
    User,
    HackathonUserAssociation,
    HackathonGroupAssociation,
    Group,
    GroupUserAssociation,
)
from core.models.hackathon_group_association import TeamStatus
from core.models.hackathon_user_association import (
    ParticipationStatus,
)


def serialize_hackathons(hackathons):
    return [
        {
            "id": hackathon.id,
            "title": hackathon.title,
            "description": hackathon.description,
            "start_time": (
                hackathon.start_time.isoformat() if hackathon.start_time else None
            ),
            "end_time": hackathon.end_time.isoformat() if hackathon.end_time else None,
            "status": hackathon.status,
            "max_participants": hackathon.max_participants,
            "current_participants": hackathon.current_participants,
            "created_at": (hackathon.created_at.isoformat()),
            "creator_id": hackathon.creator_id,
        }
        for hackathon in hackathons
    ]


# Ваша функция get_hackathons
async def get_hackathons(session: AsyncSession) -> list[HackathonSchema]:
    cached_hackathons = redis_client.get("hackathons")

    if cached_hackathons:
        hackathons_data = json.loads(cached_hackathons)
        return [HackathonSchema(**hackathon) for hackathon in hackathons_data]

    stmt = select(Hackathon).order_by(Hackathon.id)
    result: Result = await session.execute(stmt)
    hackathons = result.scalars().all()

    hackathon_schemas = [
        HackathonSchema.model_validate(hackathon) for hackathon in hackathons
    ]

    redis_client.set(
        "hackathons", json.dumps(serialize_hackathons(hackathon_schemas)), ex=30
    )

    return hackathon_schemas


async def get_hackathon(session: AsyncSession, hackathon_id: int) -> Hackathon | None:
    return await session.get(Hackathon, hackathon_id)


async def get_hackathon_by_tittle(
    session: AsyncSession, hackathon_title: str
) -> Hackathon | None:
    result = await session.execute(
        select(Hackathon).where(Hackathon.title.ilike(hackathon_title))
    )
    return result.scalars().first()


async def create_hackathon(
    hackathon_in: HackathonCreateSchema,
    session: AsyncSession,
    user_id: int,
) -> Hackathon:
    hackathon = Hackathon(**hackathon_in.model_dump(), creator_id=user_id)
    session.add(hackathon)
    await session.commit()
    return hackathon


async def get_hackathons_for_user(
    session: AsyncSession,
    user_id: int,
):
    stmt = (
        select(Hackathon)
        .where(Hackathon.users_details.any(user_id=user_id))
        .options(
            selectinload(Hackathon.tasks),
        )
    )
    result = await session.execute(stmt)
    hackathons = result.scalars().all()
    if not hackathons:
        raise HTTPException(
            status_code=404, detail="No hackathons found for the current user."
        )
    return list(hackathons)


async def get_hackathon_for_creator(session: AsyncSession, user_id: int):
    stmt = select(Hackathon).where(Hackathon.creator_id == user_id)
    result = await session.execute(stmt)
    hackathons = result.scalars().all()
    if not hackathons:
        raise HTTPException(
            status_code=404, detail="No hackathons found for the current user."
        )
    return list(hackathons)


async def update_hackathon(
    hackathon_in: HackathonUpdatePartial,
    session: AsyncSession,
    hackathon: Hackathon,
):
    # if hackathon.status != "PLANNED":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail=f"update data is prohibited when the hackathon is started.",
    #     )
    for name, value in hackathon_in.model_dump(exclude_unset=True).items():
        setattr(hackathon, name, value)
    await session.commit()
    return hackathon


async def add_user_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
    user: User,
):
    # if hackathon.status != "PLANNED":
    #   raise HTTPException(
    #      status_code=status.HTTP_403_FORBIDDEN,
    #     detail=f"acceptance of applications to the hackathon {hackathon.id} is completed",
    # )
    if user.user_role.value != "PARTICIPANT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="creators can't be in hackathon members",
        )
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
    if hackathon.current_participants == hackathon.max_participants:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No available spots in the hackathon.",
        )
    association = HackathonUserAssociation(
        hackathon_id=hackathon.id,
        user_id=user.id,
        user_status=ParticipationStatus.REGISTERED,
    )
    hackathon.current_participants += 1
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
        hackathon.current_participants -= 1
        await session.delete(association)
        await session.commit()
        return {"delete": True}
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
