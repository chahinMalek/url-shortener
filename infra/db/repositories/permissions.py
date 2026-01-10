from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.users import Permission, User
from core.repositories.permissions import PermissionRepository
from infra.db.models import UserModel
from infra.db.models.permission import UserPermissionModel


class PostgresPermissionRepository(PermissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_user_entity(self, model: UserModel) -> User:
        return User(
            user_id=model.user_id,
            email=model.email,
            password_hash=model.password_hash,
            permissions=[Permission(p.permission) for p in model.permissions],
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login,
        )

    async def get_by_user_id(self, user_id: str) -> list[Permission]:
        result = await self.session.execute(
            select(UserPermissionModel.permission).where(UserPermissionModel.user_id == user_id)
        )
        return [Permission(p) for p in result.scalars().all()]

    async def get_users_with_permission(self, permission: Permission) -> list[User]:
        result = await self.session.execute(
            select(UserModel)
            .join(UserPermissionModel)
            .where(UserPermissionModel.permission == permission.value)
        )
        models = result.scalars().all()
        return [self._to_user_entity(m) for m in models]

    async def grant(self, user_id: str, permission: Permission) -> None:
        permission_model = UserPermissionModel(user_id=user_id, permission=permission.value)
        self.session.add(permission_model)
        await self.session.flush()

    async def revoke(self, user_id: str, permission: Permission) -> None:
        await self.session.execute(
            delete(UserPermissionModel).where(
                UserPermissionModel.user_id == user_id,
                UserPermissionModel.permission == permission.value,
            )
        )
        await self.session.flush()
