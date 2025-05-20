from datetime import datetime
import logging

from typing import List, Optional

from core.models.group import GroupStatus
from .dependencies2 import act_group
from fastapi import HTTPException, status
from sqlalchemy import select, Result, func
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import json
from api_v1.hackathons.schemas import (
    HackathonCreateSchema,
    HackathonUpdatePartial,
    HackathonSchema,
    HackathonBaseSchema,
)
from core.config import redis_client, settings
from core.models import (
    Hackathon,
    User,
    HackathonUserAssociation,
    HackathonGroupAssociation,
    Group,
    GroupUserAssociation,
)
from core.models.hackathon import HackathonStatus
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
            "logo_url": hackathon.logo_url,
            "allow_teams": hackathon.allow_teams,
            "updated_at": hackathon.updated_at.isoformat(),
        }
        for hackathon in hackathons
    ]


async def get_hackathons(session: AsyncSession) -> list[HackathonSchema]:
    cached_hackathons = redis_client.get("hackathons")

    if cached_hackathons:
        hackathons_data = json.loads(cached_hackathons)
        return [HackathonSchema(**hackathon) for hackathon in hackathons_data]

    stmt = (
        select(Hackathon).where(Hackathon.is_archived == False).order_by(Hackathon.id)
    )
    result: Result = await session.execute(stmt)
    hackathons = result.scalars().all()

    hackathon_schemas = [
        HackathonSchema.model_validate(hackathon) for hackathon in hackathons
    ]

    redis_client.set(
        "hackathons", json.dumps(serialize_hackathons(hackathon_schemas)), ex=50
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

    hackathon = Hackathon(
        **hackathon_in.model_dump(),
        creator_id=user_id,
        logo_url=f"{settings.s3.domain_url}/default_logo.jpg",
    )
    stmt = (
        select(func.count())
        .select_from(Hackathon)
        .where(Hackathon.creator_id == user_id)
        .where(Hackathon.status != HackathonStatus.PLANNED)
    )
    count = await session.scalar(stmt)
    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The maximum number of hackathons created has been exceeded (max 20)",
        )
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


async def update_hackathon_logo(
    session: AsyncSession,
    hackathon: HackathonSchema,
    logo_url: str,
) -> HackathonSchema:
    hackathon.logo_url = logo_url
    await session.commit()
    return hackathon


async def get_hackathon_for_creator(session: AsyncSession, user_id: int):
    stmt = select(Hackathon).where(Hackathon.creator_id == user_id)
    result = await session.execute(stmt)
    hackathons = result.scalars().all()
    if not hackathons:
        raise HTTPException(
            status_code=404, detail="No hackathons found for the current user."
        )
    return list(hackathons)


async def update_hack(
    hackathon_in: HackathonUpdatePartial,
    session: AsyncSession,
    hackathon: Hackathon,
    user: User,
) -> HackathonSchema:
    if hackathon.status != HackathonStatus.PLANNED and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Обновление данных запрещено, когда хакатон уже начался или завершен.",
        )

    update_data = hackathon_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value == "string":
            continue

        if field == "max_participants":
            if value <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Количество участников должно быть больше нуля.",
                )
            if value < hackathon.current_participants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Нельзя установить максимальное количество участников ({value}) "
                    f"меньше текущего количества ({hackathon.current_participants}).",
                )
        setattr(hackathon, field, value)

    await session.commit()
    await session.refresh(hackathon)

    return HackathonSchema.model_validate(hackathon)


async def activate_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
):
    if (
        hackathon.status == HackathonStatus.PLANNED
        or hackathon.status == HackathonStatus.CANCELED
    ):
        hackathon.status = HackathonStatus.ACTIVE
        hackathon.updated_at = datetime.now()
    if hackathon.status == HackathonStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="hackathon completed"
        )
    await session.commit()
    await session.refresh(hackathon)

    return {"success": f"hackathon {hackathon.title} activate"}


async def cancel_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
):
    if (
        hackathon.status == HackathonStatus.ACTIVE
        or hackathon.status == HackathonStatus.PLANNED
    ):
        hackathon.status = HackathonStatus.CANCELED
        hackathon.updated_at = datetime.now()
    if hackathon.status == HackathonStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="hackathon completed"
        )
    await session.commit()
    await session.refresh(hackathon)
    return {"success": f"hackathon {hackathon.title} deactivate"}


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
    if user.user_role.value == "CREATOR" and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="creators can't be in hackathon members",
        )
    if hackathon.status == HackathonStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="hackathon begin. you dont can patch",
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
    association = await session.scalar(
        select(HackathonUserAssociation)
        .where(HackathonUserAssociation.hackathon_id == hackathon.id)
        .where(HackathonUserAssociation.user_id == user.id)
    )

    if association or user.is_superuser and hackathon.status != HackathonStatus.ACTIVE:
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
    if not hackathon.allow_teams:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="teams are not allowed to participate in the hackathon",
        )
    if group.status == GroupStatus.BANNED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Group {group.id} BANNED",
        )
    if group.status == "INACTIVE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Group {group.id} INACTIVE",
        )
    if hackathon.status != HackathonStatus.PLANNED:
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
    await act_group(session=session, group=group)
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


async def delete_hackathon(hackathon_id: int, session: AsyncSession):
    stmt = (
        select(Hackathon)
        .where(Hackathon.id == hackathon_id)
        .options(
            selectinload(Hackathon.tasks),
            selectinload(Hackathon.users_details),
            selectinload(Hackathon.groups_details),
        )
    )
    hackathon = (await session.execute(stmt)).scalars().first()

    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден"
        )

    await session.delete(hackathon)
    await session.commit()

    return {
        "status": "success",
        "message": "Хакатон и все связанные данные успешно удалены",
        "hackathon_id": hackathon_id,
    }


async def patch_max_users_in_hack(
    session: AsyncSession, hackathon: Hackathon, max_participants: int, user: User
) -> HackathonSchema:
    if hackathon.status != HackathonStatus.PLANNED and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Updating max participants is only allowed for planned hackathons.",
        )

    if max_participants <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of participants must be greater than zero.",
        )

    if max_participants < hackathon.current_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot set maximum participants ({max_participants}) "
            f"less than current participants ({hackathon.current_participants}).",
        )

    hackathon.max_participants = max_participants
    await session.commit()
    await session.refresh(hackathon)

    return HackathonSchema.model_validate(hackathon)


async def archive(session: AsyncSession, hackathon: Hackathon):
    if hackathon.status == HackathonStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="hackathon not completed"
        )
    hackathon.is_archived = True
    await session.commit()
    return {"ok": f"contest {hackathon.id} is archived"}


async def unarchive(session: AsyncSession, hackathon: Hackathon):
    hackathon.is_archived = False
    await session.commit()
    return {"ok": f"hackathon {hackathon.id} is unarchived"}


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
