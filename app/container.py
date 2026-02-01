from functools import lru_cache

from infra.config import AppConfig
from infra.services.db_service import DatabaseService


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()


config = get_config()

db_service = DatabaseService(
    connection_string=config.database_url,
    echo=config.database_echo,
)
