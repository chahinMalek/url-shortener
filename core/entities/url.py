from dataclasses import dataclass, field
from datetime import UTC, datetime

from core.enums.safety_status import SafetyStatus


@dataclass
class Url:
    short_code: str
    long_url: str
    owner_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    safety_status: SafetyStatus = field(default_factory=lambda: SafetyStatus.PENDING)
    threat_score: float | None = None
    classified_at: datetime | None = None
    classifier: str | None = None
