from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api_v1.test_cases.schemas import CreateTestSchema, TestSchema
from core.models import TestCase, ContestTask
from api_v1.hackathons.dependencies import get_hackathon


async def create_test_for_hackathon(
    session: AsyncSession,
    test_data: CreateTestSchema,
    hackathon_id: int,
    task_id: int,
) -> TestSchema:
    hackathon = await get_hackathon(session, hackathon_id)
    if hackathon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    task = await session.scalar(select(ContestTask).where(ContestTask.id == task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена"
        )
    test = TestCase(
        input=test_data.input,
        expected_output=test_data.expected_output,
        task_id=task_id,
        is_public=test_data.is_public,
    )
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return TestSchema.model_validate(test)


async def get_tests(
    session: AsyncSession,
):
    result = await session.execute(select(TestCase))
    result = result.scalars().all()
    return [test for test in result]
