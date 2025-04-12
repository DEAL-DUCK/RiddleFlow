from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from core.models import Jury, Hackathon, JuryHackathonAssociation, User, jury
from .schemas import JuryResponse
from fastapi import HTTPException, status
def any_not(ann: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'{ann} not found.')

async def add_jury_to_hackathon(
        session: AsyncSession,
        user_id: int,
        hackathon_id: int,
) -> JuryResponse:
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()
    if not user: any_not('user')
    hackathon = await session.execute(select(Hackathon).where(Hackathon.id == hackathon_id))
    hackathon = hackathon.scalar_one_or_none()
    if not hackathon: any_not('hackathon')
    jury = await session.execute(select(Jury).where(Jury.user_id == user_id))
    jury = jury.scalar_one_or_none()
    if not jury:
        jury = Jury(user_id=user_id)
        session.add(jury)
        try:
            await session.commit()
            await session.refresh(jury)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create jury record",
            )

    existing_assoc = await session.execute(
        select(JuryHackathonAssociation).where(
            JuryHackathonAssociation.jury_id == jury.id,
            JuryHackathonAssociation.hackathon_id == hackathon_id
        )
    )

    if existing_assoc.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a jury member for this hackathon",
        )

    try:
        association = JuryHackathonAssociation(
            jury_id=jury.id,
            hackathon_id=hackathon_id
        )
        session.add(association)
        await session.commit()
        await session.refresh(association)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add jury to hackathon: {str(e)}",
        )

    return JuryResponse(
        status="success",
        jury_id=jury.id,
        hackathon_id=hackathon_id,
        user_id=user_id,
    )


async def remove_jury_from_hackathon(
        session: AsyncSession,
        jury_id: int,
        hackathon_id: int,
) -> dict:

    hackathon = await session.execute(select(Hackathon).where(Hackathon.id == hackathon_id))
    if not hackathon.scalar_one_or_none(): any_not('hackathon')
    jury = await session.execute(select(Jury).where(Jury.id == jury_id))
    if not jury.scalar_one_or_none(): any_not('jury')
    try:
        result = await session.execute(
            delete(JuryHackathonAssociation)
            .where(
                JuryHackathonAssociation.jury_id == jury_id,
                JuryHackathonAssociation.hackathon_id == hackathon_id
            )
        )
        await session.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This jury is not assigned to the specified hackathon"
            )

        return {
            "status": "success",
            "message": "Jury removed from hackathon successfully",
            "jury_id": jury_id,
            "hackathon_id": hackathon_id
        }

    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
async def what_hackathon_sudit(
        session: AsyncSession,
        jury_id: int,
):
    if await session.get(Jury,jury_id) is None: return any_not('jury')
    hackathons = await session.execute(
        select(Jury)
        .where(Jury.jury_id == jury_id)
        .where
    )

async def get_hackathons_judged_by_jury(session: AsyncSession, jury_id: int):
    result = await session.execute(
        select(Hackathon)
        .join(JuryHackathonAssociation, Hackathon.id == JuryHackathonAssociation.hackathon_id)
        .where(JuryHackathonAssociation.jury_id == jury_id)
    )
    return list(result.scalars().all())


