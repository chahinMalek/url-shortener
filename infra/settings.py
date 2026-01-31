from importlib.metadata import version

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(
        default="URL Shortener",
        description="Application display name",
    )
    app_version: str = Field(
        default_factory=lambda: version("url-shortener"),
        description="Application version from package metadata",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode (disable in production)",
    )
    environment: str = Field(
        default="development",
        description="Environment name (development, staging, production)",
    )

    # Database settings
    database_url: str = Field(
        ...,
        description="PostgreSQL async connection string (required, e.g., postgresql+asyncpg://user:pass@host:5432/db)",
    )
    database_echo: bool = Field(
        default=False,
        description="Echo SQL statements to stdout (useful for debugging)",
    )

    # Redis settings
    redis_url: str = Field(
        ...,
        description="Redis connection string (e.g., redis://redis:6379/db)",
    )

    # Auth settings
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT signing. Generate with: openssl rand -hex 32",
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        le=1440,  # Max 24 hours
        description="Access token expiration time in minutes",
    )

    classifier_model_path: str = Field(
        default="assets/models/online_classifier_xgb_v1.0.0.onnx",
        description="Path to the ONNX model file for online URL classification",
    )
