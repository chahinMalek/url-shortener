import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.notification import Notification
from infra.db.repositories.notifications import PostgresNotificationRepository


@pytest.mark.unit
class TestPostgresNotificationRepository:
    @pytest.fixture
    def repository(self, db_session: AsyncSession):
        return PostgresNotificationRepository(db_session)

    async def test_add_notification(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        notification = Notification(
            user_id="user_1",
            notification_type="url_flagged_malicious",
            message="Your URL was flagged",
            details={"short_code": "abc123"},
        )

        added = await repository.add(notification)
        await db_session.commit()

        assert added.id is not None
        assert added.user_id == "user_1"
        assert added.notification_type == "url_flagged_malicious"
        assert added.message == "Your URL was flagged"
        assert added.details == {"short_code": "abc123"}
        assert added.is_read is False

    async def test_get_by_id(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        notification = Notification(
            user_id="user_1",
            notification_type="url_flagged_malicious",
            message="Test message",
        )
        added = await repository.add(notification)
        await db_session.commit()

        found = await repository.get_by_id(added.id)

        assert found is not None
        assert found.id == added.id
        assert found.message == "Test message"

    async def test_get_by_id_not_found(self, repository: PostgresNotificationRepository):
        found = await repository.get_by_id(99999)
        assert found is None

    async def test_get_by_user_id(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        for i in range(3):
            notification = Notification(
                user_id="user_1",
                notification_type="url_flagged_malicious",
                message=f"Message {i}",
            )
            await repository.add(notification)
        await db_session.commit()

        notifications = await repository.get_by_user_id("user_1")

        assert len(notifications) == 3

    async def test_get_by_user_id_with_limit(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        for i in range(5):
            notification = Notification(
                user_id="user_1",
                notification_type="url_flagged_malicious",
                message=f"Message {i}",
            )
            await repository.add(notification)
        await db_session.commit()

        notifications = await repository.get_by_user_id("user_1", limit=2)

        assert len(notifications) == 2

    async def test_get_by_user_id_unread_only(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        # Add 2 unread notifications
        for i in range(2):
            notification = Notification(
                user_id="user_1",
                notification_type="url_flagged_malicious",
                message=f"Unread {i}",
            )
            await repository.add(notification)

        # Add 1 read notification
        read_notification = Notification(
            user_id="user_1",
            notification_type="url_flagged_malicious",
            message="Read",
            is_read=True,
        )
        await repository.add(read_notification)
        await db_session.commit()

        unread = await repository.get_by_user_id("user_1", unread_only=True)

        assert len(unread) == 2
        for n in unread:
            assert n.is_read is False

    async def test_get_by_user_id_empty(self, repository: PostgresNotificationRepository):
        notifications = await repository.get_by_user_id("nonexistent_user")
        assert notifications == []

    async def test_mark_as_read(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        notification = Notification(
            user_id="user_1",
            notification_type="url_flagged_malicious",
            message="To be marked read",
        )
        added = await repository.add(notification)
        await db_session.commit()

        assert added.is_read is False

        updated = await repository.mark_as_read(added.id)
        await db_session.commit()

        assert updated is not None
        assert updated.is_read is True

    async def test_mark_as_read_not_found(self, repository: PostgresNotificationRepository):
        result = await repository.mark_as_read(99999)
        assert result is None

    async def test_mark_all_as_read(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        for i in range(3):
            notification = Notification(
                user_id="user_1",
                notification_type="url_flagged_malicious",
                message=f"Message {i}",
            )
            await repository.add(notification)
        await db_session.commit()

        count = await repository.mark_all_as_read("user_1")
        await db_session.commit()

        assert count == 3

        unread_count = await repository.get_unread_count("user_1")
        assert unread_count == 0

    async def test_get_unread_count(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        # Add 2 unread
        for i in range(2):
            notification = Notification(
                user_id="user_1",
                notification_type="url_flagged_malicious",
                message=f"Unread {i}",
            )
            await repository.add(notification)

        # Add 1 read
        read_notification = Notification(
            user_id="user_1",
            notification_type="url_flagged_malicious",
            message="Read",
            is_read=True,
        )
        await repository.add(read_notification)
        await db_session.commit()

        count = await repository.get_unread_count("user_1")

        assert count == 2

    async def test_get_unread_count_zero(self, repository: PostgresNotificationRepository):
        count = await repository.get_unread_count("nonexistent_user")
        assert count == 0

    async def test_notifications_ordered_by_created_at_desc(
        self, repository: PostgresNotificationRepository, db_session: AsyncSession
    ):
        for i in range(3):
            notification = Notification(
                user_id="user_1",
                notification_type="url_flagged_malicious",
                message=f"Message {i}",
            )
            await repository.add(notification)
            await db_session.flush()

        await db_session.commit()

        notifications = await repository.get_by_user_id("user_1")

        # Most recent should be first (descending order)
        assert len(notifications) == 3
        for i in range(len(notifications) - 1):
            assert notifications[i].created_at >= notifications[i + 1].created_at
