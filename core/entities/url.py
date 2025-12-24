from dataclasses import dataclass
from datetime import datetime


@dataclass
class Url:
    short_code: str
    long_url: str
    owner_id: str
    created_at: datetime
    is_active: bool = True
