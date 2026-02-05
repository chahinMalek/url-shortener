from typing import Protocol

from core.entities.notification import Notification


class NotificationRepository(Protocol):
    async def add(self, notification: Notification) -> Notification: ...

    async def get_by_id(self, notification_id: int) -> Notification | None: ...

    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
    ) -> list[Notification]: ...

    async def mark_as_read(self, notification_id: int) -> Notification | None: ...

    async def mark_all_as_read(self, user_id: str) -> int: ...

    async def get_unread_count(self, user_id: str) -> int: ...
