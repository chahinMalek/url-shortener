from datetime import UTC, datetime

import pytest

from core.entities.users import Permission, User


@pytest.mark.unit
class TestUserEntity:
    def test_user_creation(self):
        now = datetime.now(UTC)

        user = User(
            user_id="user_1",
            email="test@example.com",
            password_hash="hash",
            permissions=[Permission.SHORTEN_URL],
            created_at=now,
        )

        assert user.user_id == "user_1"
        assert user.email == "test@example.com"
        assert user.permissions == [Permission.SHORTEN_URL]
        assert user.created_at == now
        assert user.is_active is True

    def test_has_permission(self):
        user = User(
            user_id="user_1",
            email="test@example.com",
            password_hash="hash",
            permissions=[Permission.SHORTEN_URL, Permission.DELETE_URL],
        )

        assert user.has_permission(Permission.SHORTEN_URL) is True
        assert user.has_permission(Permission.DELETE_URL) is True
        assert user.has_permission(Permission.MANAGE_USERS) is False

    def test_has_any_permission(self):
        user = User(
            user_id="user_1",
            email="test@example.com",
            password_hash="hash",
            permissions=[Permission.SHORTEN_URL],
        )

        assert user.has_any_permission([Permission.SHORTEN_URL, Permission.DELETE_URL]) is True
        assert user.has_any_permission([Permission.DELETE_URL, Permission.MANAGE_USERS]) is False

    def test_has_all_permissions(self):
        user = User(
            user_id="user_1",
            email="test@example.com",
            password_hash="hash",
            permissions=[Permission.SHORTEN_URL, Permission.DELETE_URL],
        )

        assert user.has_all_permissions([Permission.SHORTEN_URL, Permission.DELETE_URL]) is True
        assert user.has_all_permissions([Permission.SHORTEN_URL, Permission.MANAGE_USERS]) is False

    def test_update_last_login(self):
        user = User(user_id="user_1", email="test@example.com", password_hash="hash")
        assert user.last_login is None

        user.update_last_login()

        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)
