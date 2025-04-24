from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_v1.auth.fastapi_users import current_active_user, current_active_superuser
from api_v1.hackathons.schemas import HackathonBaseSchema, HackathonSchema
from core.models import User, Hackathon


async def is_this_user_admin(
    user: User = Depends(current_active_user),
):
    if user.is_superuser:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"user {user.id} is not admin",
    )
async def get_all_hackathons(session: AsyncSession) -> list[HackathonSchema]:
    stmt = select(Hackathon).order_by(Hackathon.id)
    result = await session.execute(stmt)
    hackathons = result.scalars().all()
    return [
        HackathonSchema(
            id=hackathon.id,
            title=hackathon.title,
            description=hackathon.description,
            start_time=hackathon.start_time,
            end_time=hackathon.end_time,
            status=hackathon.status.value,
            max_participants=hackathon.max_participants,
            current_participants=hackathon.current_participants,
            created_at=hackathon.created_at,
            updated_at=hackathon.updated_at,
            allow_teams=hackathon.allow_teams,
            logo_url=hackathon.logo_url or '',
            creator_id=hackathon.creator_id
        )
        for hackathon in hackathons
    ]