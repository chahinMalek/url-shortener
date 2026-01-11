import re

from core.entities.url import SafetyStatus
from core.services.classification.classifier.base import BaseUrlClassifier
from core.services.classification.result import ClassificationResult


class PatternMatchUrlClassifier(BaseUrlClassifier):
    def __init__(
        self,
        version: str,
        patterns: list[str],
    ):
        self._version = version
        self._patterns = patterns[:]

    @property
    def version(self) -> str:
        return self._version

    @property
    def name(self) -> str:
        return self.__class__.__name__

    async def classify(self, url: str) -> ClassificationResult:
        for pattern in self._patterns:
            if re.match(pattern, url):
                return ClassificationResult(
                    status=SafetyStatus.MALICIOUS,
                    threat_score=1.0,
                    classifier_version=self.key,
                )
        return ClassificationResult(
            status=SafetyStatus.PENDING,
            threat_score=0.0,
            classifier_version=self.key,
        )
