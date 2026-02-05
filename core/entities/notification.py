from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class Notification:
    user_id: str
    notification_type: str
    message: str
    id: int | None = None
    details: dict[str, Any] = field(default_factory=dict)
    is_read: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
