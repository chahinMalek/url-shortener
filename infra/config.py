from importlib.metadata import version
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# constants
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # db settings
    database_url: str
    database_echo: bool

    # app settings
    app_name: str
    app_version: str = version("url-shortener")
    debug: bool
    environment: str = "development"

    # auth settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
