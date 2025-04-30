#чтобы не было циклических импортов
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Group
from ..groups.crud import activate_group

async def act_group(
        session : AsyncSession,
        group : Group
):
    return await activate_group(session=session,group=group)
