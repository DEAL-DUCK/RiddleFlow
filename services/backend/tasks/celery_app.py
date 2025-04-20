import datetime
import enum
import asyncio
import logging

from celery.schedules import crontab
from celery import Celery
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.models import Hackathon
from core.config import settings

celery_app = Celery(
    main=settings.celery.CELERY_MAIN,
    broker=settings.celery.CELERY_BROKER,
    backend=settings.celery.CELERY_BACKEND,
)

# Создайте асинхронный движок и сессию
DATABASE_URL = "postgresql+asyncpg://user:password@pg:5432/RiddleFlowDB"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class HackathonStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def check_hackathon_times_async():
    async with AsyncSessionLocal() as session:
        stmt = select(Hackathon)
        result = await session.execute(stmt)
        hackathons = result.scalars().all()
        for hackathon in hackathons:
            now = datetime.datetime.now()  # TODO: ПОМЕНЯТЬ НА UTC!!!!
            logging.info(f"{hackathon.status}")
            if str(hackathon.status) == str(HackathonStatus.PLANNED) and (
                hackathon.start_time <= now < hackathon.end_time
            ):
                hackathon.status = "ACTIVE"
                logging.info(
                    f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA, \n id = {hackathon.id}, \n start = {hackathon.start_time}, \n now = {now}"
                )
            if str(hackathon.status) == str(HackathonStatus.ACTIVE) and (
                now > hackathon.end_time
            ):
                hackathon.status = "COMPLETED"
                logging.info(
                    f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA, \n id = {hackathon.id}, \n start = {hackathon.end_time}, \n now = {now}"
                )
        await session.commit()  # Коммит после завершения всех изменений


@celery_app.task
def check_hackathon_times():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_hackathon_times_async())


celery_app.conf.beat_schedule = {
    "check-hackathon-times-every-minute": {
        "task": "tasks.celery_app.check_hackathon_times",
        "schedule": crontab(),  # Запускать каждую минуту
    },
}
