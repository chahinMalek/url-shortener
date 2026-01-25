from typing import Protocol, runtime_checkable

from core.entities.classifier_result import ClassifierResult


@runtime_checkable
class BaseUrlClassifier(Protocol):
    @property
    def key(self) -> str: ...

    async def classify(self, url: str) -> ClassifierResult: ...
