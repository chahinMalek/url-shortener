from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from core.entities.classification_result import ClassificationResult
from core.enums.safety_status import SafetyStatus


class TestClassificationResult:
    def test_init_defaults(self):
        now = datetime.now(UTC)

        with patch("core.entities.classification_result.datetime") as mock_datetime:
            mock_datetime.now.return_value = now
            result = ClassificationResult(
                status=SafetyStatus.SAFE,
                threat_score=0.1,
                classifier="test-v1.0.0",
            )

            assert result.timestamp == now
            assert result.status == SafetyStatus.SAFE
            assert result.threat_score == 0.1
            assert result.classifier == "test-v1.0.0"
            assert result.latency_ms is None
            assert result.success is True
            assert result.error is None
            assert result.details is None

    def test_init_with_latency_and_details(self):
        result = ClassificationResult(
            status=SafetyStatus.MALICIOUS,
            threat_score=0.95,
            classifier="test-v1.0.0",
            latency_ms=12.5,
            details={"confidence": 0.95, "model": "xgboost"},
        )

        assert result.latency_ms == 12.5
        assert result.details == {"confidence": 0.95, "model": "xgboost"}
        assert result.success is True

    def test_create_fail_validation_threat_score(self):
        with pytest.raises(ValueError, match="threat_score must be between 0.0 and 1.0"):
            ClassificationResult(
                status=SafetyStatus.SAFE,
                threat_score=1.5,
                classifier="test-v1.0.0",
            )

    def test_failure_factory_method(self):
        result = ClassificationResult.failure(
            classifier="test-v1.0.0",
            error="Connection timeout",
            latency_ms=5000.0,
        )

        assert result.success is False
        assert result.error == "Connection timeout"
        assert result.latency_ms == 5000.0
        assert result.status == SafetyStatus.PENDING
        assert result.threat_score == 0.0
        assert result.classifier == "test-v1.0.0"

    def test_is_malicious(self):
        result = ClassificationResult(
            status=SafetyStatus.MALICIOUS,
            threat_score=0.95,
            classifier="test-v1.0.0",
        )
        assert result.is_malicious is True
        assert result.is_safe is False

    def test_is_safe(self):
        result = ClassificationResult(
            status=SafetyStatus.SAFE,
            threat_score=0.1,
            classifier="test-v1.0.0",
        )
        assert result.is_safe is True
        assert result.is_malicious is False

    def test_is_pending(self):
        result = ClassificationResult(
            status=SafetyStatus.PENDING,
            threat_score=0.5,
            classifier="test-v1.0.0",
        )
        assert result.is_pending is True

    def test_is_suspicious(self):
        result = ClassificationResult(
            status=SafetyStatus.SUSPICIOUS,
            threat_score=0.6,
            classifier="test-v1.0.0",
        )
        assert result.is_suspicious is True

    def test_from_classifier_result(self):
        from core.entities.classifier_result import ClassifierResult

        classifier_result = ClassifierResult(
            status=SafetyStatus.MALICIOUS,
            threat_score=0.85,
            classifier="pattern-match-v1.0.0",
            details={"pattern": "phishing"},
        )

        result = ClassificationResult.from_classifier_result(
            classifier_result,
            latency_ms=15.3,
        )

        assert result.status == SafetyStatus.MALICIOUS
        assert result.threat_score == 0.85
        assert result.classifier == "pattern-match-v1.0.0"
        assert result.details == {"pattern": "phishing"}
        assert result.latency_ms == 15.3
        assert result.success is True
        assert result.error is None

    def test_from_classifier_result_with_custom_timestamp(self):
        from core.entities.classifier_result import ClassifierResult

        classifier_result = ClassifierResult(
            status=SafetyStatus.SAFE,
            threat_score=0.05,
            classifier="test-v1.0.0",
        )

        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        result = ClassificationResult.from_classifier_result(
            classifier_result,
            timestamp=custom_time,
        )

        assert result.timestamp == custom_time
