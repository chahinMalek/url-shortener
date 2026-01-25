from dataclasses import dataclass

from core.enums.safety_status import SafetyStatus


@dataclass
class ClassifierResult:
    """
    Internal data model returned by classifiers.
    Contains the core classification information without metadata.
    """

    status: SafetyStatus
    threat_score: float
    classifier: str
    details: dict | None = None

    def __post_init__(self):
        if not 0.0 <= self.threat_score <= 1.0:
            raise ValueError(f"threat_score must be between 0.0 and 1.0, got {self.threat_score}")

    @property
    def is_malicious(self) -> bool:
        return self.status == SafetyStatus.MALICIOUS

    @property
    def is_safe(self) -> bool:
        return self.status == SafetyStatus.SAFE

    @property
    def is_pending(self) -> bool:
        return self.status == SafetyStatus.PENDING

    @property
    def is_suspicious(self) -> bool:
        return self.status == SafetyStatus.SUSPICIOUS
