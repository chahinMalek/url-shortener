from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.url import Url
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
        )

    def _to_model(self, entity: Url) -> UrlModel:
        return UrlModel(
            short_code=entity.short_code,
            long_url=entity.long_url,
            owner_id=entity.owner_id,
            created_at=entity.created_at,
            is_active=entity.is_active,
        )

    async def add(self, url: Url) -> Url:
        model = self._to_model(url)
        self.session.add(model)
        await self.session.flush()
        return url

    async def get_by_code(self, short_code: str) -> Url | None:
        result = await self.session.execute(
            select(UrlModel).where(
                UrlModel.short_code == short_code,
                UrlModel.is_active.is_(True),
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
