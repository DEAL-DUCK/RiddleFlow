import datetime
import enum
import logging

import docker
from celery import Celery
from celery.schedules import crontab
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from core.config import settings
from core.models import Hackathon, ContestSubmission, ContestTask, TestCase, Contest

celery_app = Celery(
    main=settings.celery.celery_main,
    broker=settings.celery.celery_broker,
    backend=settings.celery.celery_backend,
)

DATABASE_URL = "postgresql://user:password@pg:5432/RiddleFlowDB"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


class HackathonStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class ContestStatus(enum.Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
docker_client = docker.from_env()


def run_code_safely(code: str, timeout: int, memory: str, test_case: list):
    """Запускает каждый тест в новом контейнере и удаляет его сразу после проверки."""
    for test in test_case:
        container = None
        try:
            # Создаём контейнер для текущего теста
            container = docker_client.containers.run(
                image="python:3.9-slim",
                command=["python", "-c", code],
                mem_limit=memory,
                network_mode="none",
                stdin_open=True,
                detach=True,
                tty=True,
            )

            # Отправляем входные данные
            socket = container.attach_socket(params={"stdin": 1, "stream": 1})
            input_data = f"{test.input.strip()}\n".encode("utf-8")
            socket._sock.send(input_data)

            # Ждём завершения (с таймаутом)
            container.wait(timeout=timeout / 1000 + 1)

            # Получаем логи и берём последнюю непустую строку
            logs = container.logs().decode("utf-8").splitlines()
            output = next((line for line in reversed(logs) if line.strip()), "")

            # Проверяем результат
            if str(output) != test.expected_output:
                return {
                    "test_input": test.input,
                    "success": False,
                    "user_output": output,
                    "expected_output": test.expected_output,
                }
        except docker.errors.ContainerError as e:
            return {
                "success": False,
                "output": e.stderr.decode().strip() if e.stderr else str(e),
                "exit_code": 1,
                "error": "Container error",
            }
        except Exception as e:
            return {
                "success": False,
                "output": str(e),
                "exit_code": 1,
                "error": "Execution error",
            }
        finally:
            # Удаляем контейнер сразу после проверки теста
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception as e:
                    logging.error(f"Ошибка при удалении контейнера: {e}")

    # Все тесты пройдены успешно
    return {"success": True}


@celery_app.task(bind=True, name="evaluate_submission")
def check_code(self, submission_id):
    with SessionLocal() as session:
        try:
            # Получаем submission и задачу
            submission = session.execute(
                select(ContestSubmission).where(ContestSubmission.id == submission_id)
            ).scalar_one()

            task = session.execute(
                select(ContestTask).where(ContestTask.id == submission.task_id)
            ).scalar_one()
            tests = session.execute(
                select(TestCase).where(TestCase.task_id == submission.task_id)
            )
            test_case = [test for test in tests.scalars().all()]
            exec_result = run_code_safely(
                code=submission.code,
                timeout=task.time_limit,
                memory=f"{task.memory_limit}m",
                test_case=test_case,
            )
            return {
                "submission_id": submission_id,
                "task_id": task.id,
                "status": "COMPLETED" if exec_result["success"] else "FAILED",
                "result": exec_result,
                "timestamp": datetime.datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "submission_id": submission_id,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.datetime.now().isoformat(),
            }


@celery_app.task
def check_hackathon_times():
    with SessionLocal() as session:
        stmt1 = select(Hackathon)
        stmt2 = select(Contest)
        result1 = session.execute(stmt1)
        result2 = session.execute(stmt2)
        hackathons = result1.scalars().all()
        contests = result2.scalars().all()
        for hackathon in hackathons:
            now = datetime.datetime.now(datetime.UTC)
            logging.info(f"{hackathon.status}")
            if str(hackathon.status) == str(HackathonStatus.PLANNED) and (
                hackathon.start_time <= now < hackathon.end_time
            ):
                hackathon.status = "ACTIVE"
                logging.info(
                    f"id = {hackathon.id}, \n start = {hackathon.start_time}, \n now = {now}"
                )
            if (
                str(hackathon.status) == str(HackathonStatus.ACTIVE)
                or str(hackathon.status) == str(HackathonStatus.PLANNED)
            ) and (now > hackathon.end_time):
                hackathon.status = "COMPLETED"
                logging.info(
                    f"id = {hackathon.id}, \n start = {hackathon.end_time}, \n now = {now}"
                )

        for contest in contests:
            now = datetime.datetime.now(datetime.UTC)
            logging.info(f"{contest.status}")
            if str(contest.status) == str(ContestStatus.PLANNED) and (
                contest.start_time <= now < contest.end_time
            ):
                contest.status = "ACTIVE"
                logging.info(
                    f"id = {contest.id}, \n start = {contest.start_time}, \n now = {now}"
                )
            if (
                str(contest.status) == str(ContestStatus.ACTIVE)
                or str(contest.status) == str(ContestStatus.PLANNED)
            ) and (now > contest.end_time):
                contest.status = "COMPLETED"
                logging.info(
                    f"id = {contest.id}, \n start = {contest.end_time}, \n now = {now}"
                )
        session.commit()


celery_app.conf.beat_schedule = {
    "check-hackathon-times-every-minute": {
        "task": "tasks.celery_app.check_hackathon_times",
        "schedule": crontab(),
    },
}
