import asyncio

from services.backend.src.core.models.db_helper import db_helper
from services.backend.src.core.models.base import Base
from services.backend.src.core.models.user import User
from services.backend.src.core.models.jury import Jury,jury_hackathon_association
from services.backend.src.core.models.jury import JuryEvaluation
from services.backend.src.core.models.submission import Submission
from services.backend.src.core.models.hackathon import Hackathon
async def init_models():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
    print("Таблицы созданы успешно!")