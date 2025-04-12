import asyncio
from services.backend.src.core.models import Base
from services.backend.src.core.models.db_helper import db_helper


async def init_models():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_models())
    print("Таблицы успешно пересозданы!")