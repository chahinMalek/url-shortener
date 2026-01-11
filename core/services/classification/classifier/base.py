from typing import Protocol, runtime_checkable

from core.services.classification.result import ClassificationResult


@runtime_checkable
class BaseUrlClassifier(Protocol):
    @property
    def version(self) -> str: ...

    @property
    def name(self) -> str: ...

    @property
    def key(self) -> str:
        return f"{self.name}-v{self.version}"

    async def classify(self, url: str) -> ClassificationResult: ...
