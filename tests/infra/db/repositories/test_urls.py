from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.url import Url
from core.enums.safety_status import SafetyStatus
from infra.db.repositories.urls import PostgresUrlRepository


@pytest.mark.unit
class TestPostgresUrlRepository:
    @pytest.fixture
    def repository(self, db_session: AsyncSession):
        return PostgresUrlRepository(db_session)

    async def test_add_url(self, repository: PostgresUrlRepository, db_session: AsyncSession):
        url = Url(
            short_code="test1234",
            long_url="https://example.com",
            owner_id="user_1",
        )

        added_url = await repository.add(url)
        await db_session.commit()

        assert added_url.short_code == "test1234"
        assert added_url.long_url == "https://example.com"
        assert added_url.owner_id == "user_1"
        assert added_url.safety_status == SafetyStatus.PENDING
        assert added_url.threat_score is None
        assert added_url.classified_at is None
        assert isinstance(added_url.created_at, datetime)

    async def test_get_by_code(self, repository: PostgresUrlRepository, db_session: AsyncSession):
        url = Url(
            short_code="getme123",
            long_url="https://test.com",
            owner_id="user_1",
        )
        await repository.add(url)
        await db_session.commit()

        found_url = await repository.get_by_code("getme123")

        assert found_url is not None
        assert found_url.short_code == "getme123"
        assert found_url.long_url == "https://test.com"

    async def test_get_by_code_not_found(self, repository: PostgresUrlRepository):
        found_url = await repository.get_by_code("nonexistent")

        assert found_url is None

    async def test_get_by_code_returns_inactive_url(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url = Url(
            short_code="inactive",
            long_url="https://inactive.com",
            owner_id="user_1",
            is_active=False,
        )
        await repository.add(url)
        await db_session.commit()

        found_url = await repository.get_by_code("inactive")

        assert found_url is not None
        assert found_url.short_code == "inactive"
        assert found_url.is_active is False

    async def test_set_safety_status_safe(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url = Url(
            short_code="safe1234",
            long_url="https://safe.com",
            owner_id="user_1",
        )
        await repository.add(url)
        await db_session.commit()

        updated = await repository.set_safety_status(
            "safe1234", SafetyStatus.SAFE, threat_score=0.1, classifier="v1.0"
        )

        assert updated is not None
        assert updated.safety_status == SafetyStatus.SAFE
        assert updated.threat_score == 0.1
        assert updated.classifier == "v1.0"
        assert updated.classified_at is not None

    async def test_set_safety_status_malicious(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url = Url(
            short_code="mal12345",
            long_url="https://malicious.com",
            owner_id="user_1",
        )
        await repository.add(url)
        await db_session.commit()

        updated = await repository.set_safety_status(
            "mal12345", SafetyStatus.MALICIOUS, threat_score=0.95, classifier="v1.0"
        )

        assert updated is not None
        assert updated.safety_status == SafetyStatus.MALICIOUS
        assert updated.threat_score == 0.95

    async def test_set_safety_status_pending_raises(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url = Url(
            short_code="pend1234",
            long_url="https://pending.com",
            owner_id="user_1",
        )
        await repository.add(url)
        await db_session.commit()

        with pytest.raises(ValueError, match="Cannot set safety status to PENDING"):
            await repository.set_safety_status(
                "pend1234", SafetyStatus.PENDING, threat_score=0.0, classifier="v1.0"
            )

    async def test_set_safety_status_not_found(self, repository: PostgresUrlRepository):
        result = await repository.set_safety_status(
            "nonexist", SafetyStatus.SAFE, threat_score=0.1, classifier="v1.0"
        )

        assert result is None

    async def test_reset_safety_status(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url = Url(
            short_code="reset123",
            long_url="https://reset.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.2,
            classified_at=datetime.now(UTC),
            classifier="v1.0",
        )
        await repository.add(url)
        await db_session.commit()

        reset = await repository.reset_safety_status("reset123")

        assert reset is not None
        assert reset.safety_status == SafetyStatus.PENDING
        assert reset.threat_score is None
        assert reset.classified_at is None
        assert reset.classifier is None

    async def test_reset_safety_status_not_found(self, repository: PostgresUrlRepository):
        result = await repository.reset_safety_status("nonexist")

        assert result is None

    async def test_disable_url(self, repository: PostgresUrlRepository, db_session: AsyncSession):
        url = Url(
            short_code="dis12345",
            long_url="https://disable.com",
            owner_id="user_1",
        )
        await repository.add(url)
        await db_session.commit()

        disabled = await repository.disable("dis12345")

        assert disabled is not None
        assert disabled.is_active is False

    async def test_enable_url(self, repository: PostgresUrlRepository, db_session: AsyncSession):
        url = Url(
            short_code="ena12345",
            long_url="https://enable.com",
            owner_id="user_1",
            is_active=False,
        )
        await repository.add(url)
        await db_session.commit()

        enabled = await repository.enable("ena12345")

        assert enabled is not None
        assert enabled.is_active is True

    async def test_disable_not_found(self, repository: PostgresUrlRepository):
        result = await repository.disable("nonexist")

        assert result is None

    async def test_enable_not_found(self, repository: PostgresUrlRepository):
        result = await repository.enable("nonexist")

        assert result is None

    async def test_get_pending_urls(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url1 = Url(short_code="pend0001", long_url="https://pending1.com", owner_id="user_1")
        url2 = Url(short_code="pend0002", long_url="https://pending2.com", owner_id="user_1")
        url3 = Url(short_code="pend0003", long_url="https://pending3.com", owner_id="user_1")
        safe_url = Url(
            short_code="safe0001",
            long_url="https://safe.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=datetime.now(UTC),
            classifier="v1.0",
        )
        await repository.add(url1)
        await repository.add(url2)
        await repository.add(url3)
        await repository.add(safe_url)
        await db_session.commit()

        pending = await repository.get_pending_urls(limit=10)

        assert len(pending) == 3
        assert all(u.safety_status == SafetyStatus.PENDING for u in pending)

    async def test_get_pending_urls_with_limit(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url1 = Url(short_code="lim00001", long_url="https://limit1.com", owner_id="user_1")
        url2 = Url(short_code="lim00002", long_url="https://limit2.com", owner_id="user_1")
        url3 = Url(short_code="lim00003", long_url="https://limit3.com", owner_id="user_1")
        url4 = Url(short_code="lim00004", long_url="https://limit4.com", owner_id="user_1")
        url5 = Url(short_code="lim00005", long_url="https://limit5.com", owner_id="user_1")
        await repository.add(url1)
        await repository.add(url2)
        await repository.add(url3)
        await repository.add(url4)
        await repository.add(url5)
        await db_session.commit()

        pending = await repository.get_pending_urls(limit=2)

        assert len(pending) == 2

    async def test_get_pending_urls_with_cursor(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        url1 = Url(short_code="cur00001", long_url="https://cursor1.com", owner_id="user_1")
        url2 = Url(short_code="cur00002", long_url="https://cursor2.com", owner_id="user_1")
        url3 = Url(short_code="cur00003", long_url="https://cursor3.com", owner_id="user_1")
        url4 = Url(short_code="cur00004", long_url="https://cursor4.com", owner_id="user_1")
        url5 = Url(short_code="cur00005", long_url="https://cursor5.com", owner_id="user_1")
        await repository.add(url1)
        await repository.add(url2)
        await repository.add(url3)
        await repository.add(url4)
        await repository.add(url5)
        await db_session.commit()

        batch1 = await repository.get_pending_urls(limit=2)
        assert len(batch1) == 2

        cursor = batch1[-1].short_code
        batch2 = await repository.get_pending_urls(limit=2, start_after=cursor)

        assert len(batch2) == 2
        assert all(u.short_code > cursor for u in batch2)

    async def test_get_pending_urls_empty(self, repository: PostgresUrlRepository):
        pending = await repository.get_pending_urls()

        assert pending == []

    async def test_get_by_safety_status_safe(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        now = datetime.now(UTC)
        url1 = Url(
            short_code="safe0001",
            long_url="https://safe1.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=0),
            classifier="v1.0",
        )
        url2 = Url(
            short_code="safe0002",
            long_url="https://safe2.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=1),
            classifier="v1.0",
        )
        url3 = Url(
            short_code="safe0003",
            long_url="https://safe3.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=2),
            classifier="v1.0",
        )
        await repository.add(url1)
        await repository.add(url2)
        await repository.add(url3)
        await db_session.commit()

        safe_urls = await repository.get_by_safety_status(SafetyStatus.SAFE)

        assert len(safe_urls) == 3
        assert all(u.safety_status == SafetyStatus.SAFE for u in safe_urls)

    async def test_get_by_safety_status_pending_raises(self, repository: PostgresUrlRepository):
        with pytest.raises(ValueError, match="Cannot use get_by_safety_status"):
            await repository.get_by_safety_status(SafetyStatus.PENDING)

    async def test_get_by_safety_status_scanned_before(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        now = datetime.now(UTC)
        old_url = Url(
            short_code="old00001",
            long_url="https://old.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(days=7),
            classifier="v1.0",
        )
        recent_url = Url(
            short_code="new00001",
            long_url="https://new.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=1),
            classifier="v1.0",
        )
        await repository.add(old_url)
        await repository.add(recent_url)
        await db_session.commit()

        cutoff = now - timedelta(days=1)
        old_urls = await repository.get_by_safety_status(SafetyStatus.SAFE, scanned_before=cutoff)

        assert len(old_urls) == 1
        assert old_urls[0].short_code == "old00001"

    async def test_get_by_safety_status_scanned_after(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        now = datetime.now(UTC)
        old_url = Url(
            short_code="old00002",
            long_url="https://old2.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(days=7),
            classifier="v1.0",
        )
        recent_url = Url(
            short_code="new00002",
            long_url="https://new2.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=1),
            classifier="v1.0",
        )
        await repository.add(old_url)
        await repository.add(recent_url)
        await db_session.commit()

        cutoff = now - timedelta(days=1)
        recent_urls = await repository.get_by_safety_status(SafetyStatus.SAFE, scanned_after=cutoff)

        assert len(recent_urls) == 1
        assert recent_urls[0].short_code == "new00002"

    async def test_get_by_safety_status_sort_order_asc(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        now = datetime.now(UTC)
        url1 = Url(
            short_code="sort0000",
            long_url="https://sort0.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=0),
            classifier="v1.0",
        )
        url2 = Url(
            short_code="sort0001",
            long_url="https://sort1.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=1),
            classifier="v1.0",
        )
        url3 = Url(
            short_code="sort0002",
            long_url="https://sort2.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=2),
            classifier="v1.0",
        )
        await repository.add(url1)
        await repository.add(url2)
        await repository.add(url3)
        await db_session.commit()

        urls = await repository.get_by_safety_status(SafetyStatus.SAFE, sort_order="asc")

        # Oldest first (largest timedelta)
        assert urls[0].short_code == "sort0002"
        assert urls[-1].short_code == "sort0000"

    async def test_get_by_safety_status_sort_order_desc(
        self, repository: PostgresUrlRepository, db_session: AsyncSession
    ):
        now = datetime.now(UTC)
        url1 = Url(
            short_code="desc0000",
            long_url="https://desc0.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=0),
            classifier="v1.0",
        )
        url2 = Url(
            short_code="desc0001",
            long_url="https://desc1.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=1),
            classifier="v1.0",
        )
        url3 = Url(
            short_code="desc0002",
            long_url="https://desc2.com",
            owner_id="user_1",
            safety_status=SafetyStatus.SAFE,
            threat_score=0.1,
            classified_at=now - timedelta(hours=2),
            classifier="v1.0",
        )
        await repository.add(url1)
        await repository.add(url2)
        await repository.add(url3)
        await db_session.commit()

        urls = await repository.get_by_safety_status(SafetyStatus.SAFE, sort_order="desc")

        # Most recent first (smallest timedelta)
        assert urls[0].short_code == "desc0000"
        assert urls[-1].short_code == "desc0002"
