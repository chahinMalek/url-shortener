from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class SafetyStatus(str, Enum):
    PENDING = "pending"
    SAFE = "safe"
    MALICIOUS = "malicious"
    SUSPICIOUS = "suspicious"


@dataclass
class Url:
    short_code: str
    long_url: str
    owner_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    safety_status: SafetyStatus = field(default_factory=lambda: SafetyStatus.PENDING)
    threat_score: float | None = None
    last_scanned_at: datetime | None = None
    classifier_version: str | None = None
