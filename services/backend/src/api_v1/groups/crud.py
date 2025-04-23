from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from api_v1.groups.schemas import GroupCreateSchema, GroupUpdateSchema, GroupSchema
from core.config import settings
from core.models import Group, User, GroupUserAssociation
from core.models.group_user_association import ParticipationStatus


async def get_groups(session: AsyncSession) -> list[Group]:
    stmt = select(Group).order_by(Group.id)
    result: Result = await session.execute(stmt)
    groups = result.scalars().all()
    return list(groups)


async def get_group(session: AsyncSession, group_id: int) -> Group | None:
    return await session.get(Group, group_id)


async def create_group(
    session: AsyncSession,
    group_in: GroupCreateSchema,
    user_id: int,
) -> Group:
    group = Group(
        **group_in.model_dump(),
        logo_url=f"{settings.s3.domain_url}/default_logo.jpg",
        owner_id=user_id,
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
    association = GroupUserAssociation(
        group_id=group.id,
        user_id=user.id,
    )
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
