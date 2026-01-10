from datetime import datetime
from typing import Literal, Protocol

from core.entities.url import SafetyStatus, Url


class UrlRepository(Protocol):
    async def add(self, url: Url) -> Url: ...

    async def get_by_code(self, code: str) -> Url | None: ...

    async def get_by_safety_status(
        self,
        status: SafetyStatus,
        limit: int = 100,
        scanned_before: datetime | None = None,
        scanned_after: datetime | None = None,
        start_after: str | None = None,
        sort_order: Literal["asc", "desc"] = "asc",
    ) -> list[Url]: ...

    async def get_pending_urls(
        self,
        limit: int = 100,
        start_after: str | None = None,
    ) -> list[Url]: ...

    async def set_safety_status(
        self,
        short_code: str,
        status: SafetyStatus,
        threat_score: float,
        classifier_version: str,
    ) -> Url | None: ...

    async def reset_safety_status(self, short_code: str) -> Url | None: ...

    async def enable(self, short_code: str) -> Url | None: ...

    async def disable(self, short_code: str) -> Url | None: ...
