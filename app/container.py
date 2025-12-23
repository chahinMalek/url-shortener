from app.config import get_settings
from infra.services.db_service import DatabaseService

settings = get_settings()

db_service = DatabaseService(
    connection_string=settings.database_url,
    echo=settings.database_echo,
)
