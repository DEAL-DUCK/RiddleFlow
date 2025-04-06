from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from api_v1 import router as router_v1
from core.config import settings
from core.models import db_helper
from core.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with db_helper.db_helper.engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api.prefix)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
