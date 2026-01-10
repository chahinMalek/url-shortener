import re

from core.entities.url import SafetyStatus
from core.services.classification.classifier.base import BaseUrlClassifier
from core.services.classification.result import ClassificationResult


class PatternMatchClassifier(BaseUrlClassifier):
    VERSION = "1.0.0"

    def __init__(self, patterns: list[str]):
        self.patterns = patterns[:]

    async def classify(self, url: str) -> ClassificationResult:
        for pattern in self.patterns:
            if re.match(pattern, url):
                return ClassificationResult(
                    status=SafetyStatus.MALICIOUS,
                    threat_score=1.0,
                    classifier_version=self.get_version(),
                )
        return ClassificationResult(
            status=SafetyStatus.PENDING,
            threat_score=0.0,
            classifier_version=self.get_version(),
        )

    def get_version(self) -> str:
        return f"{self.__class__.__name__}-{self.VERSION}"
