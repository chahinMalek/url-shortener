from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Url:
    short_code: str
    long_url: str
    owner_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
