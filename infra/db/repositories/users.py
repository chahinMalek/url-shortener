from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.users import Permission, User
from core.repositories.users import UserRepository
from infra.db.models import UserModel


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            user_id=model.user_id,
            email=model.email,
            password_hash=model.password_hash,
            permissions=[Permission(p) for p in model.permissions],
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login,
        )

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            user_id=user.user_id,
            email=user.email,
            password_hash=user.password_hash,
            permissions=[p.value for p in user.permissions],
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )

    async def add(self, user: User) -> User:
        model = self._to_model(user)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.user_id == user_id))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        updated_at = datetime.now(UTC)
        result = await self.session.execute(
            update(UserModel)
            .where(UserModel.user_id == user.user_id)
            .values(
                email=user.email,
                password_hash=user.password_hash,
                permissions=[p.value for p in user.permissions],
                is_active=user.is_active,
                updated_at=updated_at,
                last_login=user.last_login,
            )
            .returning(UserModel)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User with id {user.user_id} not found")
        await self.session.flush()
        return self._to_entity(model)

    async def delete(self, user_id: str) -> bool:
        result = await self.session.execute(delete(UserModel).where(UserModel.user_id == user_id))
        await self.session.flush()
        return result.rowcount > 0
