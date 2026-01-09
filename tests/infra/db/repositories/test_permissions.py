import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.permissions import Permission
from infra.db.models.user import UserModel
from infra.db.repositories.permissions import PostgresPermissionRepository


@pytest.mark.unit
class TestPostgresPermissionRepository:
    @pytest.fixture
    def repository(self, db_session: AsyncSession):
        return PostgresPermissionRepository(db_session)

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        user = UserModel(user_id="user_perm_test", email="perm@test.com", password_hash="pw")
        db_session.add(user)
        await db_session.flush()
        return user

    async def test_grant_and_get_permissions(
        self, repository: PostgresPermissionRepository, test_user: UserModel
    ):
        await repository.grant(test_user.user_id, Permission.SHORTEN_URL)
        await repository.grant(test_user.user_id, Permission.VIEW_ANALYTICS)

        permissions = await repository.get_by_user_id(test_user.user_id)
        assert len(permissions) == 2
        assert Permission.SHORTEN_URL in permissions
        assert Permission.VIEW_ANALYTICS in permissions

    async def test_get_users_with_permission(
        self, repository: PostgresPermissionRepository, test_user: UserModel
    ):
        await repository.grant(test_user.user_id, Permission.MANAGE_USERS)

        users = await repository.get_users_with_permission(Permission.MANAGE_USERS)

        assert len(users) >= 1
        assert any(u.user_id == test_user.user_id for u in users)
        assert users[0].email == test_user.email

    async def test_revoke_permission(
        self, repository: PostgresPermissionRepository, test_user: UserModel
    ):
        await repository.grant(test_user.user_id, Permission.DELETE_URL)
        assert Permission.DELETE_URL in await repository.get_by_user_id(test_user.user_id)

        await repository.revoke(test_user.user_id, Permission.DELETE_URL)
        permissions = await repository.get_by_user_id(test_user.user_id)
        assert Permission.DELETE_URL not in permissions
