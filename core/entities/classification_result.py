from dataclasses import dataclass, field
from datetime import UTC, datetime

from core.entities.classifier_result import ClassifierResult
from core.enums.safety_status import SafetyStatus


@dataclass
class ClassificationResult(ClassifierResult):
    """
    Full classification result with metadata for persistence.
    Extends ClassifierResult with additional tracking information.
    """

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    latency_ms: float | None = None
    success: bool = True
    error: str | None = None

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    latency_ms: float | None = None
    success: bool = True
    error: str | None = None

    @classmethod
    def from_classifier_result(
        cls,
        classifier_result: ClassifierResult,
        latency_ms: float | None = None,
        timestamp: datetime | None = None,
    ) -> "ClassificationResult":
        """Create a ClassificationResult from a ClassifierResult with metadata."""
        return cls(
            status=classifier_result.status,
            threat_score=classifier_result.threat_score,
            classifier=classifier_result.classifier,
            details=classifier_result.details,
            latency_ms=latency_ms,
            timestamp=timestamp or datetime.now(UTC),
            success=True,
            error=None,
        )

    @classmethod
    def failure(
        cls,
        classifier: str,
        error: str,
        latency_ms: float | None = None,
    ) -> "ClassificationResult":
        return cls(
            status=SafetyStatus.PENDING,
            threat_score=0.0,
            classifier=classifier,
            latency_ms=latency_ms,
            success=False,
            error=error,
        )
