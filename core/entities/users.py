from dataclasses import dataclass, field
from datetime import UTC, datetime

from core.permissions import Permission


@dataclass
class User:
    user_id: str
    email: str
    password_hash: str
    permissions: list[Permission] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default=datetime.now(UTC))
    updated_at: datetime | None = None
    last_login: datetime | None = None

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_any_permission(self, permissions: list[str]) -> bool:
        return any(perm in self.permissions for perm in permissions)

    def has_all_permissions(self, permissions: list[str]) -> bool:
        return all(perm in self.permissions for perm in permissions)

    def update_last_login(self) -> None:
        self.last_login = datetime.now(UTC)
