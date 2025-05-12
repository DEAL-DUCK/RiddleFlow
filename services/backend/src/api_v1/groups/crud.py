import logging

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, Result, func, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api_v1.groups.schemas import GroupCreateSchema, GroupUpdateSchema, GroupSchema,GroupStatus
from core.config import settings
from core.models import Group, User, GroupUserAssociation, HackathonGroupAssociation, Hackathon
from core.models.group_user_association import ParticipationStatus
from core.models.hackathon import HackathonStatus
from core.models.hackathon_group_association import TeamStatus
from .dependencies2 import del_group_in_hack
from ..users.schemas import UserRole


async def get_groups(session: AsyncSession) -> list[Group]:
    stmt = select(Group).order_by(Group.id)
    result: Result = await session.execute(stmt)
    groups = result.scalars().all()
    return list(groups)
async def get_my_group_for_owner(
        session : AsyncSession,
        owner_id : int
) ->list[Group]:
    stmt = select(Group).where(Group.owner_id == owner_id)
    result : Result = await session.execute(stmt)
    groups = result.scalars().all()
    return list(groups)
async def get_group(session: AsyncSession, group_id: int) -> Group | None:
    return await session.get(Group, group_id)


async def create_group(
    session: AsyncSession,
    group_in: GroupCreateSchema,
    user_id: int,
) -> Group:
    groups_count = await session.scalar(
        select(func.count(Group.id))
    )

    if groups_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of groups (10) has been reached"
        )

    existing_group = await session.execute(
        select(Group).where(Group.title == group_in.title)
    )
    if existing_group.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group with this title already exists"
        )
    group = Group(
        **group_in.model_dump(),
        logo_url=f"{settings.s3.domain_url}/default_logo.jpg",
        owner_id=user_id,
        current_members = 1

    )
    session.add(group)
    await session.commit()
    return group


async def update_group(
    session: AsyncSession,
    group_in: GroupUpdateSchema,
    group: GroupSchema,
) -> GroupSchema:
    for name, value in group_in.model_dump(exclude_unset=True).items():
        setattr(group, name, value)
    await session.commit()
    return group


async def update_group_logo(
    session: AsyncSession,
    group: GroupSchema,
    logo_url: str,
) -> GroupSchema:
    group.logo_url = logo_url
    await session.commit()
    return group


async def add_user_in_group_for_id(
    session: AsyncSession,
    group: Group,
    user: User,
):
    existing_association = await session.scalar(
        select(GroupUserAssociation)
        .where(GroupUserAssociation.group_id == group.id)
        .where(GroupUserAssociation.user_id == user.id)
    )

    if existing_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User  {user.id} is already participating in this group",
        )

    existing_association = await session.scalar(
        select(HackathonGroupAssociation)
        .join(HackathonGroupAssociation.hackathon)
        .where(
            HackathonGroupAssociation.group_id == group.id,
            Hackathon.status == HackathonStatus.ACTIVE))
    if existing_association:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Group  {group.id} is already participating  hackathon ",
        )
    if group.max_members == group.current_members:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The team has reached its maximum number of participants.",
        )
    if user.user_role.value != "PARTICIPANT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="creators can't be in group",
        )
    if group.status == GroupStatus.BANNED :
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The team id BANNED",
        )

    association = GroupUserAssociation(
        group_id=group.id,
        user_id=user.id,
    )
    group.status = "ACTIVE"
    group.updated_at = func.now()
    group.current_members += 1
    session.add(association)
    await session.commit()
    return association


async def add_user_in_group_for_username(
        session: AsyncSession,
        group: Group,
        user: User,
):

    existing_association = await session.scalar(
        select(GroupUserAssociation)
        .where(GroupUserAssociation.group_id == group.id)
        .where(GroupUserAssociation.user_id == user.id)
    )

    if existing_association and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User @{user.username} is already in this group",
        )
    if group.max_members <= group.current_members:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Group has reached maximum capacity",
        )

    if user.user_role == UserRole.CREATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only participants can join groups",
        )

    if group.status == GroupStatus.BANNED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Group is banned and cannot accept new members",
        )
    association = GroupUserAssociation(
        group_id=group.id,
        user_id=user.id,
    )

    group.status = GroupStatus.ACTIVE.value
    group.updated_at = func.now()
    group.current_members += 1

    session.add(association)
    await session.commit()
    await session.refresh(association)

    return {'ok':"True",
            'user_id': association.user_id,
            'username' : user.username}
async def delete_user_in_group(
    session: AsyncSession,
    group: Group,
    user: User,
):
    association = await session.scalar(
        select(GroupUserAssociation)
        .where(GroupUserAssociation.group_id == group.id)
        .where(GroupUserAssociation.user_id == user.id)
    )

    if association:
        await session.delete(association)
        group.current_members -= 1
        await session.commit()
        return {"delete": True}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User  {user.id} is not participating in this group",
    )


async def get_users_in_group(
    session: AsyncSession,
    group: Group,
):
    result = await session.execute(
        select(GroupUserAssociation)
        .options(selectinload(GroupUserAssociation.user))
        .where(GroupUserAssociation.group_id == group.id)
    )
    associations = result.scalars().all()
    return [
        {
            "user_info": {
                "id": assoc.user.id,
                "username": assoc.user.username,
                "email": assoc.user.email,
            }
        }
        for assoc in associations
    ]


async def de_activate_group(
        session: AsyncSession,
        group: Group,
) -> dict:
    if group.status == GroupStatus.INACTIVE:
        return {
            'status': 'info',
            'message': 'Group is already inactive',
            'new_status': 'INACTIVE'
        }

    result = await session.execute(
        select(HackathonGroupAssociation)
        .where(HackathonGroupAssociation.group_id == group.id)
        .where(HackathonGroupAssociation.group_status != TeamStatus.REFUSED)
    )
    hackathon_associations = result.scalars().all()

    for association in hackathon_associations:
        hackathon = await session.get(Hackathon, association.hackathon_id)
        if hackathon and hackathon.status != HackathonStatus.COMPLETED:
            try:
                await del_group_in_hack(
                    session=session,
                    hackathon=hackathon,
                    group=group
                )
                association.group_status = TeamStatus.REFUSED
            except HTTPException as e:
                logging.error(f"Error removing group {group.id} from hackathon {hackathon.id}: {str(e)}")
                continue

    result = await session.execute(
        select(GroupUserAssociation)
        .where(GroupUserAssociation.group_id == group.id)
    )
    user_associations = result.scalars().all()
    for user_assoc in user_associations:
        user_assoc.is_active = False
        user_assoc.updated_at = func.now()

    group.status = 'INACTIVE'
    group.updated_at = func.now()
    group.current_members = 0

    await session.commit()

    return {
        'status': 'success',
        'message': f'Group {group.title} deactivated successfully. '
                  f'Removed from {len(hackathon_associations)} hackathons.',
        'new_status': 'INACTIVE',
        'affected_hackathons': len(hackathon_associations),
        'affected_members': len(user_associations)
    }
async def activate_group(
        session: AsyncSession,
        group: Group,
) -> dict:
    group.status = "ACTIVE"
    group.updated_at = func.now()
    await session.commit()
    return {
        'status': 'success',
        'message': 'Group deactivated successfully',
        'new_status': 'ACTIVE'
        }


async def get_group_for_user_id(
        session: AsyncSession,
        user: User
) -> dict:
    owner_stmt = select(Group).where(Group.owner_id == user.id)
    owner_result = await session.execute(owner_stmt)
    owner_groups = list(owner_result.scalars().all())

    if owner_groups:
        result = []
        for group in owner_groups:

            owner_stmt = select(User.username).where(User.id == group.owner_id)
            owner_result = await session.execute(owner_stmt)
            owner_username = owner_result.scalar()
            members_stmt = (
                select(User.username)
                .join(GroupUserAssociation, GroupUserAssociation.user_id == User.id)
                .where(GroupUserAssociation.group_id == group.id)
            )
            members_result = await session.execute(members_stmt)

            members = []
            if owner_username:
                members.append({
                    "username": owner_username,
                    "role": "OWNER"
                })

            for (username,) in members_result:
                if username != owner_username:
                    members.append({
                        "username": username,
                        "role": "MEMBER"
                    })

            result.append({
                "group": group,
                "role": "OWNER",
                "group_members": members
            })

        return result[0] if len(result) == 1 else result
    member_stmt = (
        select(GroupUserAssociation, Group)
        .join(Group, GroupUserAssociation.group_id == Group.id)
        .where(GroupUserAssociation.user_id == user.id)
    )
    member_result = await session.execute(member_stmt)
    association_with_group = member_result.first()

    if association_with_group:
        association, group = association_with_group
        owner_stmt = select(User.username).where(User.id == group.owner_id)
        owner_result = await session.execute(owner_stmt)
        owner_username = owner_result.scalar()

        members_stmt = (
            select(User.username)
            .join(GroupUserAssociation, GroupUserAssociation.user_id == User.id)
            .where(GroupUserAssociation.group_id == group.id)
        )
        members_result = await session.execute(members_stmt)

        members = []
        if owner_username:
            members.append({
                "username": owner_username,
                "role": "OWNER"
            })

        for (username,) in members_result:
            if username != owner_username:
                members.append({
                    "username": username,
                    "role": "MEMBER"
                })

        return {
            "group": group,
            "role": "MEMBER",
            "group_association": association,
            "group_members": members
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User is not an owner or member of any group"
    )
async def update_group_max_members(
    session: AsyncSession,
    group: Group,
    new_max_members: int
) -> dict:

    hackathon_count = await session.scalar(
        select(func.count(HackathonGroupAssociation.group_id))
        .where(HackathonGroupAssociation.group_id == group.id)
    )

    if hackathon_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change max members for group participating in hackathons"
        )

    if new_max_members < group.current_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"New max members ({new_max_members}) cannot be less than current members count ({group.current_members})"
        )

    group.max_members = new_max_members
    group.updated_at = func.now()

    await session.commit()

    return {
        'ok': True,
        'message': f"Max members updated to {new_max_members}",
        'group_id': group.id,
        'new_max_members': new_max_members,
        'current_members': group.current_members
    }