import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from uuid import uuid4
from ..contests.crud import *
from core.models import (
    Contest,
    User,
    Group,
    ContestUserAssociation,
    ContestGroupAssociation,
    GroupUserAssociation,
)
from ..contests.schemas import ContestCreateSchema, ContestUpdatePartial
from core.config import settings


@pytest.fixture(autouse=True)
async def cleanup_db(db_session: AsyncSession):
    """Фикстура для очистки базы данных после каждого теста"""
    yield
    # Удаляем данные в правильном порядке (сначала ассоциации)
    await db_session.execute(delete(ContestUserAssociation))
    await db_session.execute(delete(ContestGroupAssociation))
    await db_session.execute(delete(GroupUserAssociation))
    await db_session.execute(delete(Group))
    await db_session.execute(delete(Contest))
    await db_session.execute(delete(User))
    await db_session.commit()


@pytest.fixture
def contest_data():
    return {
        "title": f"Test Contest {uuid4()}",
        "description": "Test description",
        "start_time": datetime.now() + timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=2),
        "max_participants": 10,
        "allow_teams": True
    }


@pytest.fixture
def user_data():
    return {
        "username": f"testuser_{uuid4()}",
        "email": f"test_{uuid4()}@example.com",
        "password": "password123",
        "user_role": "PARTICIPANT"
    }


@pytest.fixture
def group_data():
    return {
        "title": f"Test Group {uuid4()}",
        "description": "Test group description",
        "max_members": 5,
        "owner_id": 1,
        "current_members": 3
    }


class TestContestFunctions:
    @pytest.mark.asyncio
    async def test_get_contests(self, db_session: AsyncSession, contest_data, user_data):
        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()

        contest = Contest(**contest_data, creator_id=user.id)
        db_session.add(contest)
        await db_session.commit()

        contests = await get_contests(db_session)
        assert len(contests) == 2
        assert contests[0].title == contest_data["title"]

