from functools import lru_cache

from infra.config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()
