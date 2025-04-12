from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from services.backend.src.api_v1.hackathons.schemas import (
    HackathonCreateSchema,
)
from services.backend.src.core.models import Hackathon, User, HackathonUserAssociation
from services.backend.src.core.models.hackathon_user_association import (
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

    association = HackathonUserAssociation(
        hackathon_id=hackathon.id,
        user_id=user.id,
        user_role=user.role.value.upper(),
        user_status=ParticipationStatus.REGISTERED,
    )

    session.add(association)
    await session.commit()
    return association


async def delete_user_in_hackathon(
        session: AsyncSession,
        hackathon_id: int,
        user_id: int,
) -> dict:
    try:
        async with session.begin():
            association = await session.scalar(
                select(HackathonUserAssociation)
                .where(HackathonUserAssociation.hackathon_id == hackathon_id)
                .where(HackathonUserAssociation.user_id == user_id)
            )

            if not association:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} is not participating in hackathon {hackathon_id}"
                )

            await session.delete(association)
            await session.commit()
            return {"status": "success", "deleted_association_id": association.id}


    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while removing user from hackathon"
        )


from sqlalchemy.orm import selectinload


async def get_users_in_hackathon(
        session: AsyncSession,
        hackathon_id: int,
) -> list[dict]:
    try:
        stmt = (
            select(HackathonUserAssociation)
            .where(HackathonUserAssociation.hackathon_id == hackathon_id)
            .options(
                selectinload(HackathonUserAssociation.user).load_only(
                    User.id,
                    User.username,
                    User.email,
                    User.role
                )
            )
        )

        result = await session.execute(stmt)
        associations = result.scalars().all()

        return [
            {
                "user": {
                    "id": association.user.id,
                    "username": association.user.username,
                    "email": association.user.email,
                    "role": association.user.role,
                },
                "status": association.user_status.value,
                "role": association.user_role.value,
                "registration_date": association.registration_date.isoformat()
                if association.registration_date else None
            }
            for association in associations
        ]

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching hackathon participants"
        )
async def get_user_in_hackathon(
    session: AsyncSession,
    hackathon: Hackathon,
    user_id: int,
):
    # тут идет запрос в бдшку по айди хакатона и айди юзера(скопипастил, проверь чтобы верно было)
    association = await session.scalar(
        select(HackathonUserAssociation)
        .where(HackathonUserAssociation.hackathon_id == hackathon.id)
        .where(HackathonUserAssociation.user_id == user_id)
    )

    if association:
        return {
            "user": {
                "id": association.user.id,
                "username": association.user.username,
                "email": association.user.email,
                "status": association.user_status,
                "role": association.user_role,
                "created_hackathons": association.user.created_hackathons,
            },
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User  {user_id} is not participating in this hackathon",
    )


"""# пока в комментарий, потому что не реализовано ролирование
async def delete_hackathon_admin(
    session: AsyncSession,
    hackathon: Hackathon,
    user: User,
):
    await session.delete(hackathon)
    await session.commit()


# тоже в комментарий, потому что ролирование не реализовано
async def update_hackathon_admin(
    session: AsyncSession,
    hackathon: Hackathon,
    hackathon_update: HackathonUpdatePartial,
    user: User,
) -> Hackathon:
    # if user.role.value == "CREATOR":
    for name, value in hackathon_update.model_dump(exclude_unset=True).items():
        setattr(hackathon, name, value)
    await session.commit()
    return hackathon
    #
    # raise HTTPException(
    #     status_code=status.HTTP_403_FORBIDDEN,
    #     detail=f"Not enough rights",
    # )"""