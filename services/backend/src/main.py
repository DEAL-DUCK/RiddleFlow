from pathlib import Path
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from starlette.staticfiles import StaticFiles
from api_v1 import router as router_v1
from core.config import settings
from core.models import db_helper
from core.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with db_helper.engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)
    yield
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix=settings.api.prefix)
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# if __name__ == "__main__":
#     uvicorn.run(
#         "main:app",
#         host=settings.run.host,
#         port=settings.run.port,
#         reload=True,
#     )
