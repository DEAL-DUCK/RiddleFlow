from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api_v1.contests.crud import get_contests, get_contest
from api_v1.test_cases.schemas import CreateTestSchema, TestSchema
from core.models import TestCase, ContestTask
from api_v1.hackathons.dependencies import get_hackathon


async def create_test_for_contest(
    session: AsyncSession,
    test_data: CreateTestSchema,
    contest_id: int,
    task_id: int,
) -> TestSchema:
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
