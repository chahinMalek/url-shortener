from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.classification_result import ClassificationResult
from core.entities.url import Url
from core.enums.safety_status import SafetyStatus
from infra.db.repositories.classification_results import PostgresClassificationResultRepository
from infra.db.repositories.urls import PostgresUrlRepository


@pytest.mark.unit
class TestPostgresClassificationRepository:
    @pytest.fixture
    def repository(self, db_session: AsyncSession):
        return PostgresClassificationResultRepository(db_session)

    @pytest.fixture
    def url_repository(self, db_session: AsyncSession):
        return PostgresUrlRepository(db_session)

    async def test_add_classification_result(
        self,
        repository: PostgresClassificationResultRepository,
        url_repository: PostgresUrlRepository,
        db_session: AsyncSession,
    ):
        # Must have a URL first due to FK
        url = Url(short_code="test1234", long_url="https://example.com", owner_id="user_1")
        await url_repository.add(url)
        await db_session.commit()

        result = ClassificationResult(
            status=SafetyStatus.SAFE,
            threat_score=0.1,
            classifier="test_classifier",
            latency_ms=123.4,
            details={"key": "value"},
        )

        added = await repository.add("test1234", result)
        await db_session.commit()

        assert added.status == SafetyStatus.SAFE
        assert added.threat_score == 0.1
        assert added.classifier == "test_classifier"
        assert added.latency_ms == 123.4
        assert added.details == {"key": "value"}

    async def test_get_latest_by_short_code(
        self,
        repository: PostgresClassificationResultRepository,
        url_repository: PostgresUrlRepository,
        db_session: AsyncSession,
    ):
        url = Url(short_code="test5678", long_url="https://example.com", owner_id="user_1")
        await url_repository.add(url)

        r1 = ClassificationResult(
            status=SafetyStatus.PENDING,
            threat_score=0.0,
            classifier="c1",
            timestamp=datetime(2025, 1, 1, tzinfo=UTC),
        )
        r2 = ClassificationResult(
            status=SafetyStatus.SAFE,
            threat_score=0.1,
            classifier="c2",
            timestamp=datetime(2025, 1, 2, tzinfo=UTC),
        )

        await repository.add("test5678", r1)
        await repository.add("test5678", r2)
        await db_session.commit()

        latest = await repository.get_latest_by_short_code("test5678")
        assert latest is not None
        assert latest.classifier == "c2"
        assert latest.status == SafetyStatus.SAFE

    async def test_get_by_short_code(
        self,
        repository: PostgresClassificationResultRepository,
        url_repository: PostgresUrlRepository,
        db_session: AsyncSession,
    ):
        url = Url(short_code="history", long_url="https://example.com", owner_id="user_1")
        await url_repository.add(url)

        for i in range(3):
            await repository.add(
                "history",
                ClassificationResult(
                    status=SafetyStatus.SAFE,
                    threat_score=0.1,
                    classifier=f"c{i}",
                ),
            )
        await db_session.commit()

        history = await repository.get_by_short_code("history")
        assert len(history) == 3
        # Should be ordered by timestamp desc
        assert history[0].classifier == "c2"
        assert history[2].classifier == "c0"
