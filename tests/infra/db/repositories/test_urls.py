from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.url import Url
from infra.db.repositories.urls import PostgresUrlRepository


@pytest.mark.unit
class TestPostgresUrlRepository:
    @pytest.fixture
    def repository(self, db_session: AsyncSession):
        return PostgresUrlRepository(db_session)

    async def test_add_url(self, repository: PostgresUrlRepository, db_session: AsyncSession):
        url = Url(short_code="test1234", long_url="https://example.com", owner_id="user_1")
        added_url = await repository.add(url)

        await db_session.commit()

        assert added_url.short_code == "test1234"
        assert added_url.long_url == "https://example.com"
        assert added_url.owner_id == "user_1"
        assert isinstance(added_url.created_at, datetime)

    async def test_get_by_code(self, repository: PostgresUrlRepository, db_session: AsyncSession):
        url = Url(short_code="getme123", long_url="https://test.com", owner_id="user_2")

        await repository.add(url)
        await db_session.commit()
        found_url = await repository.get_by_code("getme123")

        assert found_url is not None
        assert found_url.short_code == "getme123"
        assert found_url.long_url == "https://test.com"

    async def test_get_by_code_not_found(self, repository: PostgresUrlRepository):
        found_url = await repository.get_by_code("nonexistent")

        assert found_url is None

    async def test_get_inactive_url(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url = Url(
            short_code="inactive",
            long_url="https://inactive.com",
            owner_id="user_3",
            is_active=False,
        )
        await repository.add(url)
        await db_session.commit()

        found_url = await repository.get_by_code("inactive")

        assert found_url is None
