from typing import Protocol, runtime_checkable

from core.entities.classification_result import ClassificationResult


@runtime_checkable
class BaseUrlClassifier(Protocol):
    @property
    def key(self) -> str: ...

    async def classify(self, url: str) -> ClassificationResult: ...
