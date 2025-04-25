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
    )
    group.current_members += 1
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


async def add_user_in_group(
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


async def delete_user_in_group(
    session: AsyncSession,
    group: Group,
    user: User,
):
    # Находим ассоциацию между пользователем и хакатоном
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
    # Check if group is already inactive
    if group.status == GroupStatus.INACTIVE:
        return {
            'status': 'info',
            'message': 'Group is already inactive',
            'new_status': 'INACTIVE'
        }

    # Find all active hackathon associations for this group
    result = await session.execute(
        select(HackathonGroupAssociation)
        .where(HackathonGroupAssociation.group_id == group.id)
        .where(HackathonGroupAssociation.group_status != TeamStatus.REFUSED)
    )
    hackathon_associations = result.scalars().all()

    # Remove group from all active hackathons
    for association in hackathon_associations:
        hackathon = await session.get(Hackathon, association.hackathon_id)
        if hackathon and hackathon.status != HackathonStatus.COMPLETED:
            try:
                await del_group_in_hack(
                    session=session,
                    hackathon=hackathon,
                    group=group
                )
                # Update group status in the association
                association.group_status = TeamStatus.REFUSED
            except HTTPException as e:
                logging.error(f"Error removing group {group.id} from hackathon {hackathon.id}: {str(e)}")
                continue

    # Deactivate all user associations in this group
    result = await session.execute(
        select(GroupUserAssociation)
        .where(GroupUserAssociation.group_id == group.id)
    )
    user_associations = result.scalars().all()
    for user_assoc in user_associations:
        user_assoc.is_active = False
        user_assoc.updated_at = func.now()

    # Finally deactivate the group itself
    group.status = 'INACTIVE'
    group.updated_at = func.now()
    group.current_members = 0  # Reset member count since group is inactive

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
