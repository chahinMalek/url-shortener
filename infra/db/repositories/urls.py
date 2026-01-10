from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.url import SafetyStatus, Url
from core.repositories.urls import UrlRepository
from infra.db.models import UrlModel


class PostgresUrlRepository(UrlRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: UrlModel) -> Url:
        return Url(
            short_code=model.short_code,
            long_url=model.long_url,
            owner_id=model.owner_id,
            created_at=model.created_at,
            is_active=model.is_active,
            safety_status=SafetyStatus(model.safety_status),
            threat_score=model.threat_score,
            last_scanned_at=model.last_scanned_at,
            classifier_version=model.classifier_version,
        )

    def _to_model(self, entity: Url) -> UrlModel:
        return UrlModel(
            short_code=entity.short_code,
            long_url=entity.long_url,
            owner_id=entity.owner_id,
            created_at=entity.created_at,
            is_active=entity.is_active,
            safety_status=entity.safety_status.value,
            threat_score=entity.threat_score,
            last_scanned_at=entity.last_scanned_at,
            classifier_version=entity.classifier_version,
        )

    async def add(self, url: Url) -> Url:
        model = self._to_model(url)
        self.session.add(model)
        await self.session.flush()
        return url

    async def get_by_code(self, short_code: str) -> Url | None:
        result = await self.session.execute(
            select(UrlModel).where(UrlModel.short_code == short_code)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def set_safety_status(
        self,
        short_code: str,
        status: SafetyStatus,
        threat_score: float,
        classifier_version: str,
    ) -> Url | None:
        """Updates the URL's safety status and related scan data."""

        if status == SafetyStatus.PENDING:
            raise ValueError(
                "Cannot set safety status to PENDING using this method. Use reset_safety_status instead."
            )

        result = await self.session.execute(
            update(UrlModel)
            .where(UrlModel.short_code == short_code)
            .values(
                safety_status=status.value,
                last_scanned_at=datetime.now(UTC),
                threat_score=threat_score,
                classifier_version=classifier_version,
            )
            .returning(UrlModel)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def reset_safety_status(self, short_code: str) -> Url | None:
        """Resets the URL's safety status to PENDING and clear scan data."""
        result = await self.session.execute(
            update(UrlModel)
            .where(UrlModel.short_code == short_code)
            .values(
                safety_status=SafetyStatus.PENDING.value,
                last_scanned_at=None,
                threat_score=None,
                classifier_version=None,
            )
            .returning(UrlModel)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def enable(self, short_code: str) -> Url | None:
        return await self._set_active(short_code, True)

    async def disable(self, short_code: str) -> Url | None:
        return await self._set_active(short_code, False)

    async def _set_active(self, short_code: str, is_active: bool) -> Url | None:
        result = await self.session.execute(
            update(UrlModel)
            .where(UrlModel.short_code == short_code)
            .values(is_active=is_active)
            .returning(UrlModel)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_safety_status(
        self,
        status: SafetyStatus,
        limit: int = 100,
        scanned_before: datetime | None = None,
        scanned_after: datetime | None = None,
        start_after: str | None = None,
        sort_order: Literal["asc", "desc"] = "asc",
    ) -> list[Url]:
        if status == SafetyStatus.PENDING:
            raise ValueError(
                "Cannot use get_by_safety_status() to fetch URLs with PENDING status. Use get_pending_urls() instead."
            )

        query = select(UrlModel).where(UrlModel.safety_status == status.value)

        if scanned_before is not None:
            query = query.where(UrlModel.last_scanned_at < scanned_before)

        if scanned_after is not None:
            query = query.where(UrlModel.last_scanned_at > scanned_after)

        if start_after is not None:
            query = query.where(UrlModel.short_code > start_after)

        order_col = (
            UrlModel.last_scanned_at.asc()
            if sort_order == "asc"
            else UrlModel.last_scanned_at.desc()
        )
        query = query.order_by(order_col, UrlModel.short_code).limit(limit)

        result = await self.session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get_pending_urls(
        self,
        limit: int = 100,
        start_after: str | None = None,
    ) -> list[Url]:
        query = select(UrlModel).where(UrlModel.safety_status == SafetyStatus.PENDING.value)
        if start_after is not None:
            query = query.where(UrlModel.short_code > start_after)

        query = query.order_by(UrlModel.short_code).limit(limit)
        result = await self.session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]
