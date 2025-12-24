from typing import Protocol

from core.entities.url import Url


class UrlRepository(Protocol):
    async def add(self, url: Url) -> Url: ...

    async def get_by_code(self, code: str) -> Url | None: ...
