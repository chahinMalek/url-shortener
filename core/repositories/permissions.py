from typing import Protocol

from core.entities.users import User
from core.permissions import Permission


class PermissionRepository(Protocol):
    async def get_by_user_id(self, user_id: str) -> list[Permission]:
        """Get all permissions for a specific user."""
        ...

    async def get_users_with_permission(self, permission: Permission) -> list[User]:
        """Get all users that have a specific permission."""
        ...

    async def grant(self, user_id: str, permission: Permission) -> None:
        """Grant a permission to a user."""
        ...

    async def revoke(self, user_id: str, permission: Permission) -> None:
        """Revoke a permission from a user."""
        ...
