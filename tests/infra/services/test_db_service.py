from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from infra.services.db_service import DatabaseService


@pytest.mark.unit
class TestDatabaseService:
    @pytest.fixture
    async def db_service(self):
        # fresh in-memory database for each test
        service = DatabaseService("sqlite+aiosqlite:///:memory:")
        yield service
        await service.close()

    async def test_init_db(self, db_service: DatabaseService):
        await db_service.init_db()

        # check if all expected tables exist
        async with db_service.engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            )
            tables = {row[0] for row in result.fetchall()}

            assert "users" in tables
            assert "urls" in tables
            assert "user_permissions" in tables

    async def test_get_session_success(self, db_service: DatabaseService):
        await db_service.init_db()

        async for session in db_service.get_session():
            assert isinstance(session, AsyncSession)
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    async def test_get_session_rollback_on_error(self, db_service: DatabaseService):
        await db_service.init_db()

        try:
            async for session in db_service.get_session():
                # simulate a database operation and then an error
                await session.execute(text("SELECT 1"))
                raise ValueError("Simulated error")
        except ValueError as e:
            assert str(e) == "Simulated error"

    async def test_get_session_commit_failure(self, db_service: DatabaseService):
        await db_service.init_db()

        # mock the session factory to return a mock session that fails on commit
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit.side_effect = Exception("Database commit failed")

        with patch.object(db_service, "session_factory", return_value=mock_session):
            # we must mock the __aenter__ and __aexit__ because it's used in an 'async with'
            mock_session.__aenter__.return_value = mock_session

            with pytest.raises(Exception, match="Database commit failed"):
                async for session in db_service.get_session():
                    assert session is mock_session

            # verify rollback was triggered
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
