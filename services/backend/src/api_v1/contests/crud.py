from datetime import datetime
import logging


from typing import List

from core.models.group import GroupStatus
from .dependencies2 import act_group
from fastapi import HTTPException, status
from sqlalchemy import select, Result, func
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import json
from api_v1.contests.schemas import (
    ContestCreateSchema,
    ContestUpdatePartial,
    ContestSchema,
    ContestBaseSchema,
)
from core.config import redis_client
from core.models import (
    Contest,
    User,
    ContestUserAssociation,
    ContestGroupAssociation,
    Group,
    GroupUserAssociation,
)
from core.models.contest import ContestStatus
from core.models.contest_group_association import TeamStatus
from core.models.contest_user_association import (
    ParticipationStatus,
)


def serialize_contests(contests):
    return [
        {
            "id": contest.id,
            "title": contest.title,
            "description": contest.description,
            "start_time": (
                contest.start_time.isoformat() if contest.start_time else None
            ),
            "end_time": contest.end_time.isoformat() if contest.end_time else None,
            "status": contest.status,
            "max_participants": contest.max_participants,
            "current_participants": contest.current_participants,
            "created_at": (contest.created_at.isoformat()),
            "creator_id": contest.creator_id,
        }
        for contest in contests
    ]


# Ваша функция get_contests
async def get_contests(session: AsyncSession) -> list[ContestSchema]:
    # cached_contests = redis_client.get("contests")

    # if cached_contests:
    #     contests_data = json.loads(cached_contests)
    #     return [ContestSchema(**contest) for contest in contests_data]

    stmt = select(Contest).order_by(Contest.id)
    result: Result = await session.execute(stmt)
    contests = result.scalars().all()

    contest_schemas = [ContestSchema.model_validate(contest) for contest in contests]

    # redis_client.set(
    #     "contests", json.dumps(serialize_contests(contest_schemas)), ex=30
    # )

    return contest_schemas


async def get_contest(session: AsyncSession, contest_id: int) -> Contest | None:
    return await session.get(Contest, contest_id)


async def get_contest_by_tittle(
    session: AsyncSession, contest_title: str
) -> Contest | None:
    result = await session.execute(
        select(Contest).where(Contest.title.ilike(contest_title))
    )
    return result.scalars().first()


async def create_contest(
    contest_in: ContestCreateSchema,
    session: AsyncSession,
    user_id: int,
) -> Contest:

    contest = Contest(**contest_in.model_dump(), creator_id=user_id)
    stmt = (
        select(func.count())
        .select_from(Contest)
        .where(Contest.creator_id == user_id)
        .where(Contest.status != ContestStatus.PLANNED)
    )
    count = await session.scalar(stmt)
    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The maximum number of contests created has been exceeded (max 20)",
        )
    session.add(contest)
    await session.commit()
    return contest


async def get_contests_for_user(
    session: AsyncSession,
    user_id: int,
):
    stmt = (
        select(Contest)
        .where(Contest.users_details.any(user_id=user_id))
        .options(
            selectinload(Contest.tasks),
        )
    )
    result = await session.execute(stmt)
    contests = result.scalars().all()
    if not contests:
        raise HTTPException(
            status_code=404, detail="No contests found for the current user."
        )
    return list(contests)


async def get_contest_for_creator(session: AsyncSession, user_id: int):
    stmt = select(Contest).where(Contest.creator_id == user_id)
    result = await session.execute(stmt)
    contests = result.scalars().all()
    if not contests:
        raise HTTPException(
            status_code=404, detail="No contests found for the current user."
        )
    return list(contests)


async def update_contest(
    contest_in: ContestUpdatePartial,
    session: AsyncSession,
    contest: Contest,
    user: User,
) -> ContestSchema:
    if contest.status != ContestStatus.PLANNED and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Обновление данных запрещено, когда хакатон уже начался или завершен.",
        )

    update_data = contest_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value == "string":
            continue

        if field == "max_participants":
            if value <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Количество участников должно быть больше нуля.",
                )
            if value < contest.current_participants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Нельзя установить максимальное количество участников ({value}) "
                    f"меньше текущего количества ({contest.current_participants}).",
                )
        setattr(contest, field, value)

    await session.commit()
    await session.refresh(contest)

    return ContestSchema.model_validate(contest)


async def activate_contest(
    session: AsyncSession,
    contest: Contest,
):
    if (
        contest.status == ContestStatus.PLANNED
        or contest.status == ContestStatus.CANCELED
    ):
        contest.status = ContestStatus.ACTIVE
        contest.updated_at = datetime.now()
    if contest.status == ContestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="contest completed"
        )
    await session.commit()
    await session.refresh(contest)

    return {"success": f"contest {contest.title} activate"}


async def cancel_contest(
    session: AsyncSession,
    contest: Contest,
):
    if (
        contest.status == ContestStatus.ACTIVE
        or contest.status == ContestStatus.PLANNED
    ):
        contest.status = ContestStatus.CANCELED
        contest.updated_at = datetime.now()
    if contest.status == ContestStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="contest completed"
        )
    await session.commit()
    await session.refresh(contest)
    return {"success": f"contest {contest.title} deactivate"}


async def add_user_in_contest(
    session: AsyncSession,
    contest: Contest,
    user: User,
):
    # if contest.status != "PLANNED":
    #   raise HTTPException(
    #      status_code=status.HTTP_403_FORBIDDEN,
    #     detail=f"acceptance of applications to the contest {contest.id} is completed",
    # )
    if user.user_role.value == "CREATOR" and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="creators can't be in contest members",
        )
    if contest.status == ContestStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="contest begin. you dont can patch",
        )
    existing_association = await session.scalar(
        select(ContestUserAssociation)
        .where(ContestUserAssociation.contest_id == contest.id)
        .where(ContestUserAssociation.user_id == user.id)
    )
    if existing_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User  {user.id} is already participating in this contest",
        )
    if contest.current_participants == contest.max_participants:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No available spots in the contest.",
        )
    association = ContestUserAssociation(
        contest_id=contest.id,
        user_id=user.id,
        user_status=ParticipationStatus.REGISTERED,
    )
    contest.current_participants += 1
    session.add(association)
    await session.commit()
    return association


async def delete_user_in_contest(
    session: AsyncSession,
    contest: Contest,
    user: User,
):
    association = await session.scalar(
        select(ContestUserAssociation)
        .where(ContestUserAssociation.contest_id == contest.id)
        .where(ContestUserAssociation.user_id == user.id)
    )

    if association:
        contest.current_participants -= 1
        await session.delete(association)
        await session.commit()
        return {"delete": True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User  {user.id} is not participating in this contest",
    )


async def get_users_in_contest(
    session: AsyncSession,
    contest: Contest,
):
    result = await session.execute(
        select(ContestUserAssociation)
        .options(selectinload(ContestUserAssociation.user))
        .where(ContestUserAssociation.contest_id == contest.id)
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


async def get_groups_in_contest(
    session: AsyncSession,
    contest: Contest,
):
    result = await session.execute(
        select(ContestGroupAssociation)
        .options(selectinload(ContestGroupAssociation.group))
        .where(ContestGroupAssociation.contest_id == contest.id)
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


async def add_group_in_contest(
    session: AsyncSession,
    contest: Contest,
    group: Group,
):
    if not contest.allow_teams:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="teams are not allowed to participate in the contest",
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
    if contest.status != ContestStatus.PLANNED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"acceptance of applications to the contest {contest.id} is completed",
        )
    existing_association = await session.scalar(
        select(ContestGroupAssociation)
        .where(ContestGroupAssociation.contest_id == contest.id)
        .where(ContestGroupAssociation.group_id == group.id)
    )

    if existing_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Group {group.id} is already participating in this contest",
        )
    if contest.max_participants <= contest.current_participants + group.current_members:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No available spots in the contest.",
        )
    association = ContestGroupAssociation(
        contest_id=contest.id,
        group_id=group.id,
        group_status=TeamStatus.REGISTERED,
    )
    await act_group(session=session, group=group)
    contest.current_participants += group.current_members
    session.add(association)
    await session.commit()
    result = await session.execute(
        select(GroupUserAssociation)
        .options(selectinload(GroupUserAssociation.user))
        .where(GroupUserAssociation.group_id == group.id)
    )

    users_assoc = result.scalars().all()
    for assoc in users_assoc:
        await add_user_in_contest(
            session=session,
            contest=contest,
            user=assoc.user,
        )
    return association


async def delete_group_in_contest(
    session: AsyncSession,
    contest: Contest,
    group: Group,
):
    association = await session.scalar(
        select(ContestGroupAssociation)
        .where(ContestGroupAssociation.contest_id == contest.id)
        .where(ContestGroupAssociation.group_id == group.id)
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
            await delete_user_in_contest(
                session=session,
                contest=contest,
                user=assoc.user,
            )
        contest.current_participants -= group.current_members
        return {"delete": True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Group {group.id} is not participating in this contest",
    )


async def delete_contest(contest_id: int, session: AsyncSession):
    stmt = (
        select(Contest)
        .where(Contest.id == contest_id)
        .options(
            selectinload(Contest.tasks),
            selectinload(Contest.users_details),
            selectinload(Contest.groups_details),
        )
    )
    contest = (await session.execute(stmt)).scalars().first()

    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Хакатон не найден"
        )

    await session.delete(contest)
    await session.commit()

    return {
        "status": "success",
        "message": "Хакатон и все связанные данные успешно удалены",
        "contest_id": contest_id,
    }


async def patch_max_users_in_hack(
    session: AsyncSession, contest: Contest, max_participants: int, user: User
) -> ContestSchema:
    if contest.status != ContestStatus.PLANNED and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Updating max participants is only allowed for planned contests.",
        )

    if max_participants <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of participants must be greater than zero.",
        )

    if max_participants < contest.current_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot set maximum participants ({max_participants}) "
            f"less than current participants ({contest.current_participants}).",
        )

    contest.max_participants = max_participants
    await session.commit()
    await session.refresh(contest)

    return ContestSchema.model_validate(contest)


# async def get_user_in_contest(
#     session: AsyncSession,
#     contest: Contest,
#     user_id: int,
# ):
#     # тут идет запрос в бдшку по айди хакатона и айди юзера(скопипастил, проверь чтобы верно было)
#     association = await session.scalar(
#         select(ContestUserAssociation)
#         .where(ContestUserAssociation.contest_id == contest.id)
#         .where(ContestUserAssociation.user_id == user_id)
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
#                 "created_contests": association.user.created_contests,
#             },
#         }
#
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"User  {user_id} is not participating in this contest",
#     )


# async def get_all_jury_in_contest(
#         session: AsyncSession,
#         contest_id: int,
# ):
#     if not await get_contest(session=session,contest_id=contest_id): return any_not('contest_id')
#     result = await session.execute(
#         select(JuryContestAssociation)
#         .where(JuryContestAssociation.contest_id == contest_id)
#     )
#     return list(result.scalars().all())
#
