import pytest

from core.entities.url import SafetyStatus
from core.services.classification.classifier.base import BaseUrlClassifier
from core.services.classification.classifier.pattern_match import PatternMatchClassifier


class TestPatternMatchClassifier:
    def test_implements_protocol(self):
        assert isinstance(PatternMatchClassifier(patterns=[]), BaseUrlClassifier)

    def test_patterns_copied_defensively(self):
        patterns = [r".*malware\.com.*"]
        classifier = PatternMatchClassifier(patterns=patterns)
        patterns.append(r".*new.*")
        assert len(classifier.patterns) == 1

    def test_get_version(self):
        classifier = PatternMatchClassifier(patterns=[])
        assert classifier.get_version() == "PatternMatchClassifier-1.0.0"

    @pytest.mark.asyncio
    async def test_classify_malicious(self):
        classifier = PatternMatchClassifier(patterns=[r".*malware\.com.*"])
        result = await classifier.classify("https://malware.com/page")

        assert result.status == SafetyStatus.MALICIOUS
        assert result.threat_score == 1.0

    @pytest.mark.asyncio
    async def test_classify_pending(self):
        classifier = PatternMatchClassifier(patterns=[r".*malware\.com.*"])
        result = await classifier.classify("https://example.com/page")

        assert result.status == SafetyStatus.PENDING
        assert result.threat_score == 0.0
