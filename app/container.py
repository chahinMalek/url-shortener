from functools import lru_cache

from infra.config import Settings
from infra.services.db_service import DatabaseService


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

db_service = DatabaseService(
    connection_string=settings.database_url,
    echo=settings.database_echo,
)
