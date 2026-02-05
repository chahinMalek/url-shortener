from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.notification import Notification
from core.repositories.notifications import NotificationRepository
from infra.db.models.notification import NotificationModel


class PostgresNotificationRepository(NotificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: NotificationModel) -> Notification:
        return Notification(
            id=model.id,
            user_id=model.user_id,
            notification_type=model.notification_type,
            message=model.message,
            details=model.details or {},
            is_read=model.is_read,
            created_at=model.created_at,
        )

    def _to_model(self, entity: Notification) -> NotificationModel:
        return NotificationModel(
            id=entity.id,
            user_id=entity.user_id,
            notification_type=entity.notification_type,
            message=entity.message,
            details=entity.details,
            is_read=entity.is_read,
            created_at=entity.created_at,
        )

    async def add(self, notification: Notification) -> Notification:
        model = self._to_model(notification)
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, notification_id: int) -> Notification | None:
        result = await self.session.execute(
            select(NotificationModel).where(NotificationModel.id == notification_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
    ) -> list[Notification]:
        query = select(NotificationModel).where(NotificationModel.user_id == user_id)

        if unread_only:
            query = query.where(NotificationModel.is_read == False)  # noqa: E712

        query = query.order_by(NotificationModel.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def mark_as_read(self, notification_id: int) -> Notification | None:
        result = await self.session.execute(
            update(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .values(is_read=True)
            .returning(NotificationModel)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def mark_all_as_read(self, user_id: str) -> int:
        result = await self.session.execute(
            update(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read == False)  # noqa: E712
            .values(is_read=True)
        )
        return result.rowcount

    async def get_unread_count(self, user_id: str) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.is_read == False)  # noqa: E712
        )
        return result.scalar_one()
