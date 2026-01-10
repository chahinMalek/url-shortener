from typing import Protocol, runtime_checkable

from core.services.classification.result import ClassificationResult


@runtime_checkable
class BaseUrlClassifier(Protocol):
    async def classify(self, url: str) -> ClassificationResult: ...

    def get_version(self) -> str: ...
