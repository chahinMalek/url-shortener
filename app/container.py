from functools import lru_cache

from infra.services.db_service import DatabaseService
from infra.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

db_service = DatabaseService(
    connection_string=settings.database_url,
    echo=settings.database_echo,
)
