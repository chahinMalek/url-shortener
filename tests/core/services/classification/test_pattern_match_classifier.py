import pytest

from core.entities.url import SafetyStatus
from core.services.classification.classifier.base import BaseUrlClassifier
from core.services.classification.classifier.pattern_match import PatternMatchUrlClassifier


class TestPatternMatchUrlClassifier:
    def test_implements_protocol(self):
        assert isinstance(PatternMatchUrlClassifier(patterns=[]), BaseUrlClassifier)

    def test_patterns_copied_defensively(self):
        patterns = [r".*malware\.com.*"]
        classifier = PatternMatchUrlClassifier(patterns=patterns)
        patterns.append(r".*new.*")
        assert len(classifier._patterns) == 1

    def test_get_key(self):
        classifier = PatternMatchUrlClassifier(patterns=[])
        assert classifier.key == "pattern_match_classifier_v1.0.0"

    @pytest.mark.asyncio
    async def test_classify_malicious(self):
        classifier = PatternMatchUrlClassifier(patterns=[r".*malware\.com.*"])
        result = await classifier.classify("https://malware.com/page")

        assert result.status == SafetyStatus.MALICIOUS
        assert result.threat_score == 1.0

    @pytest.mark.asyncio
    async def test_classify_pending(self):
        classifier = PatternMatchUrlClassifier(patterns=[r".*malware\.com.*"])
        result = await classifier.classify("https://example.com/page")

        assert result.status == SafetyStatus.PENDING
        assert result.threat_score == 0.0
