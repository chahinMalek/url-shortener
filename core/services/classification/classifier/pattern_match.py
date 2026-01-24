import re

from core.entities.classification_result import ClassificationResult
from core.enums.safety_status import SafetyStatus
from core.services.classification.classifier.base import BaseUrlClassifier


class PatternMatchUrlClassifier(BaseUrlClassifier):
    def __init__(self, patterns: list[str]):
        self._patterns = patterns[:]

    @property
    def key(self) -> str:
        return "pattern_match_classifier_v1.0.0"

    async def classify(self, url: str) -> ClassificationResult:
        for pattern in self._patterns:
            if re.match(pattern, url):
                return ClassificationResult(
                    status=SafetyStatus.MALICIOUS,
                    threat_score=1.0,
                    classifier=self.key,
                )
        return ClassificationResult(
            status=SafetyStatus.PENDING,
            threat_score=0.0,
            classifier=self.key,
        )
