from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from core.entities.url import SafetyStatus
from core.services.classification import ClassificationResult


class TestClassificationResult:
    def test_init(self):
        now = datetime.now(UTC)

        # create first object with patched datetime.now return value
        with patch("core.services.classification.result.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            first_result = ClassificationResult(
                status=SafetyStatus.SAFE,
                threat_score=0.1,
                classifier_version="test-v1.0.0",
            )

            assert first_result.timestamp == now
            assert first_result.status == SafetyStatus.SAFE
            assert first_result.threat_score == 0.1
            assert first_result.classifier_version == "test-v1.0.0"
            assert first_result.details is None

        second_result = ClassificationResult(
            status=SafetyStatus.SAFE,
            threat_score=0.1,
            classifier_version="test-v1.0.0",
        )

        assert second_result.timestamp > now

    def test_create_fail_validation(self):
        with pytest.raises(ValueError, match="threat_score must be between 0.0 and 1.0"):
            ClassificationResult(
                status=SafetyStatus.SAFE,
                threat_score=1.5,
                classifier_version="test-v1.0.0",
            )

    def test_is_malicious(self):
        result = ClassificationResult(
            status=SafetyStatus.MALICIOUS,
            threat_score=0.95,
            classifier_version="test-v1.0.0",
        )
        assert result.is_malicious is True

    def test_is_safe(self):
        result = ClassificationResult(
            status=SafetyStatus.SAFE,
            threat_score=0.1,
            classifier_version="test-v1.0.0",
        )
        assert result.is_safe is True

    def test_is_pending(self):
        result = ClassificationResult(
            status=SafetyStatus.PENDING,
            threat_score=0.5,
            classifier_version="test-v1.0.0",
        )
        assert result.is_pending is True

    def test_is_suspicious(self):
        result = ClassificationResult(
            status=SafetyStatus.SUSPICIOUS,
            threat_score=0.6,
            classifier_version="test-v1.0.0",
        )
        assert result.is_suspicious is True
