import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.users import Permission, User
from infra.db.repositories.users import PostgresUserRepository


@pytest.mark.unit
class TestPostgresUserRepository:
    @pytest.fixture
    def repository(self, db_session: AsyncSession):
        return PostgresUserRepository(db_session)

    async def test_add_user(self, repository: PostgresUserRepository, db_session: AsyncSession):
        user = User(
            user_id="user_123",
            email="test@example.com",
            password_hash="hashed_pw",
            permissions=[Permission.SHORTEN_URL, Permission.VIEW_ANALYTICS],
        )

        added_user = await repository.add(user)
        await db_session.commit()

        assert added_user.user_id == "user_123"
        assert added_user.email == "test@example.com"
        assert len(added_user.permissions) == 2
        assert Permission.SHORTEN_URL in added_user.permissions
        assert Permission.VIEW_ANALYTICS in added_user.permissions

    async def test_get_by_id(self, repository: PostgresUserRepository, db_session: AsyncSession):
        user = User(
            user_id="user_456",
            email="another@example.com",
            password_hash="hashed_pw",
            permissions=[Permission.DELETE_URL],
        )
        await repository.add(user)
        await db_session.commit()

        found_user = await repository.get_by_id("user_456")

        assert found_user is not None
        assert found_user.user_id == "user_456"
        assert found_user.permissions == [Permission.DELETE_URL]

    async def test_get_by_email(self, repository: PostgresUserRepository, db_session: AsyncSession):
        email = "search@example.com"
        user = User(user_id="user_789", email=email, password_hash="hashed_pw")
        await repository.add(user)
        await db_session.commit()
        found_user = await repository.get_by_email(email)

        assert found_user is not None
        assert found_user.user_id == "user_789"

    async def test_update_user(self, repository: PostgresUserRepository, db_session: AsyncSession):
        user = User(
            user_id="user_update",
            email="old@example.com",
            password_hash="old_pw",
            permissions=[Permission.SHORTEN_URL],
        )
        await repository.add(user)
        await db_session.commit()

        user.email = "new@example.com"
        user.permissions = [Permission.DELETE_URL, Permission.MANAGE_USERS]
        updated_user = await repository.update(user)
        await db_session.commit()

        assert updated_user.email == "new@example.com"
        assert len(updated_user.permissions) == 2
        assert Permission.DELETE_URL in updated_user.permissions
        assert Permission.MANAGE_USERS in updated_user.permissions
        assert Permission.SHORTEN_URL not in updated_user.permissions

    async def test_delete_user(self, repository: PostgresUserRepository, db_session: AsyncSession):
        user_id = "user_delete"
        user = User(user_id=user_id, email="delete@example.com", password_hash="pw")
        await repository.add(user)
        await db_session.commit()

        success = await repository.delete(user_id)
        await db_session.commit()

        assert success is True
        assert await repository.get_by_id(user_id) is None

    async def test_update_user_not_found(
        self, repository: PostgresUserRepository, db_session: AsyncSession
    ):
        non_existent_user = User(
            user_id="non_existent_user",
            email="notfound@example.com",
            password_hash="pw",
        )

        with pytest.raises(ValueError, match="User with id non_existent_user not found"):
            await repository.update(non_existent_user)
