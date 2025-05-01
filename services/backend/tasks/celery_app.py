import datetime
import enum
import asyncio
import logging
import docker
from celery.schedules import crontab
from celery import Celery
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from core.models import Hackathon, TestCase, ContestSubmission, ContestTask
from core.config import settings

celery_app = Celery(
    main=settings.celery.CELERY_MAIN,
    broker=settings.celery.CELERY_BROKER,
    backend=settings.celery.CELERY_BACKEND,
)

# Создайте асинхронный движок и сессию
DATABASE_URL = "postgresql+asyncpg://user:password@pg:5432/RiddleFlowDB"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class HackathonStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class SubmissionStatus2(enum.Enum):
    DRAFT = "DRAFT"  # Черновик
    SUBMITTED = "SUBMITTED"  # Отправлено
    GRADED = "GRADED"  # Проверено
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
docker_client = docker.from_env()


async def check_hackathon_times_async():
    async with AsyncSessionLocal() as session:
        stmt = select(Hackathon)
        result = await session.execute(stmt)
        hackathons = result.scalars().all()
        for hackathon in hackathons:
            now = datetime.datetime.now(datetime.UTC)
            logging.info(f"{hackathon.status}")
            if str(hackathon.status) == str(HackathonStatus.PLANNED) and (
                hackathon.start_time <= now < hackathon.end_time
            ):
                hackathon.status = "ACTIVE"
            if str(hackathon.status) == str(HackathonStatus.ACTIVE) and (
                now > hackathon.end_time
            ):
                hackathon.status = "COMPLETED"
        await session.commit()


@celery_app.task
def check_hackathon_times():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_hackathon_times_async())


async def get_task_test_cases(session: AsyncSession, task_id: int):
    stmt = select(TestCase).where(TestCase.task_id == task_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_solution_status(
    session: AsyncSession,
    submission_id: int,
    status: SubmissionStatus2,
):
    solution = await session.get(ContestSubmission, submission_id)
    if solution:
        solution.status = status
        await session.commit()


def run_code_in_docker(
    code: str, input_data: str, timeout: int = 5000, memory_limit: str = "256m"
) -> dict:
    try:
        container = docker_client.containers.run(
            "python:3.9-slim",
            command=["python", "-c", code],
            stdin_open=True,
            detach=True,
            mem_limit=memory_limit,
            cpu_period=100000,
            cpu_quota=timeout * 1000,
            network_mode="none",
        )

        exit_code = container.wait(timeout=timeout / 1000 + 1)
        output = container.logs().decode().strip()
        container.remove()

        return {
            "status": (
                SubmissionStatus2.SUBMITTED
                if exit_code == 0
                else SubmissionStatus2.RUNTIME_ERROR
            ),
            "output": output,
            "time": exit_code["StatusCode"],
        }
    except Exception as e:
        logging.error(f"Docker error: {str(e)}")
        return {"status": SubmissionStatus2.RUNTIME_ERROR, "output": str(e), "time": 0}


async def check_submission_async(submission_id: int):
    async with AsyncSessionLocal() as session:
        submission = await session.get(ContestSubmission, submission_id)
        if not submission:
            logging.error(f"Solution {submission_id} not found")
            return

        test_cases = await get_task_test_cases(session, submission.task_id)
        task = await session.get(ContestTask, submission.task_id)

        for test_case in test_cases:
            result = run_code_in_docker(
                code=submission.code,
                input_data=test_case.input,
                timeout=task.time_limit,
                memory_limit=f"{task.memory_limit}m",
            )

            if result["status"] != SubmissionStatus2.SUBMITTED:
                await update_solution_status(
                    session,
                    submission_id,
                    result["status"],
                    {"failed_test": test_case.id, "error": result["output"]},
                )
                return

            if result["output"] != test_case.expected_output:
                await update_solution_status(
                    session,
                    submission_id,
                    SubmissionStatus2.WRONG_ANSWER,
                    {"failed_test": test_case.id},
                )
                return

        await update_solution_status(
            session,
            submission_id,
            SubmissionStatus2.SUBMITTED,
            {"time": result["time"]},
        )


@celery_app.task
def check_solution(solution_id: int):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_submission_async(solution_id))


celery_app.conf.beat_schedule = {
    "check-hackathon-times-every-minute": {
        "task": "tasks.celery_app.check_hackathon_times",
        "schedule": crontab(),  # Запускать каждую минуту
    },
}
