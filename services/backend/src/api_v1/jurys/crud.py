from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from .depends import get_jury
from core.models import User, Hackathon, hackathon
from core.models.jury import Jury
def any_not(a):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

async def add_jury_in_hack(
        session: AsyncSession,
        hackathon_id: int,
        user_id: int,
):
    hackathons = await session.get(Hackathon, hackathon_id)
    jury = await get_jury(session, hackathon_id, user_id)
    if not jury:
        jury = Jury(user_id=user_id)
        session.add(jury)
        await session.flush()
    if jury in hackathons.jury_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user is already a jury member for this hackathon"
        )
    hackathons.jury_members.append(jury)
    await session.commit()
    return {"message": "Jury member added successfully", "jury_id": jury.id}
async def delete_jury_in_hack(
        session: AsyncSession,
        hackathon_id: int,
        user_id: int,
):
    jury = await get_jury(session, hackathon_id, user_id)
    hack = await session.get(Hackathon, hackathon_id)
    if jury in hack.jury_members:
        await session.delete(jury)
        return {"message": "Jury member deleted successfully",
                "jury_id": jury.id}