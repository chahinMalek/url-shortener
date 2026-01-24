from abc import ABC, abstractmethod

from core.entities.classification_result import ClassificationResult


class ClassificationResultRepository(ABC):
    @abstractmethod
    async def add(self, short_code: str, result: ClassificationResult) -> ClassificationResult:
        pass

    @abstractmethod
    async def get_by_short_code(self, short_code: str) -> list[ClassificationResult]:
        pass

    @abstractmethod
    async def get_latest_by_short_code(self, short_code: str) -> ClassificationResult | None:
        pass
