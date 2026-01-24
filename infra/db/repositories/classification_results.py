from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.entities.classification_result import ClassificationResult
from core.enums.safety_status import SafetyStatus
from core.repositories.classification_results import ClassificationResultRepository
from infra.db.models.classification_result import ClassificationResultModel


class PostgresClassificationResultRepository(ClassificationResultRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ClassificationResultModel) -> ClassificationResult:
        return ClassificationResult(
            status=SafetyStatus(model.status),
            threat_score=model.threat_score,
            classifier=model.classifier,
            timestamp=model.timestamp,
            latency_ms=model.latency_ms,
            success=model.success,
            error=model.error,
            details=model.details,
        )

    def _to_model(self, short_code: str, entity: ClassificationResult) -> ClassificationResultModel:
        return ClassificationResultModel(
            url_short_code=short_code,
            status=entity.status.value,
            threat_score=entity.threat_score,
            classifier=entity.classifier,
            timestamp=entity.timestamp,
            latency_ms=entity.latency_ms,
            success=entity.success,
            error=entity.error,
            details=entity.details,
        )

    async def add(self, short_code: str, result: ClassificationResult) -> ClassificationResult:
        model = self._to_model(short_code, result)
        self.session.add(model)
        await self.session.flush()
        return result

    async def get_by_short_code(self, short_code: str) -> list[ClassificationResult]:
        query = (
            select(ClassificationResultModel)
            .where(ClassificationResultModel.url_short_code == short_code)
            .order_by(ClassificationResultModel.timestamp.desc())
        )
        result = await self.session.execute(query)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_latest_by_short_code(self, short_code: str) -> ClassificationResult | None:
        query = (
            select(ClassificationResultModel)
            .where(ClassificationResultModel.url_short_code == short_code)
            .order_by(ClassificationResultModel.timestamp.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
