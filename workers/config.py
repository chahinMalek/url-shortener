from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery broker and result backend",
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

    # Model settings
    bert_model_path: str = Field(
        default="assets/models/urlbert_classifier_v4/urlbert_classifier_v4.onnx",
        description="Path to ONNX model file",
    )

    bert_tokenizer_path: str = Field(
        default="assets/models/urlbert_classifier_v4",
        description="Path to tokenizer directory",
    )

    # worker settings
    batch_size: int = Field(
        default=100,
        description="Number of URLs to process per task execution",
        ge=1,
        le=1000,
    )

    classification_interval_minutes: int = Field(
        default=60,
        description="Interval between classification runs (in minutes)",
        ge=1,
        le=1440,
    )

    reclassification_sample_percent: float = Field(
        default=5.0,
        description="Percentage of non-PENDING URLs to re-classify",
        ge=0.1,
        le=100.0,
    )

    task_soft_time_limit: int = Field(
        default=300,
        description="Soft time limit for tasks in seconds (raises exception)",
        ge=60,
    )

    task_time_limit: int = Field(
        default=360,
        description="Hard time limit for tasks in seconds (kills task)",
        ge=60,
    )

    celery_task_max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed tasks",
        ge=0,
        le=10,
    )

    celery_task_retry_delay: int = Field(
        default=60,
        description="Delay between retries in seconds",
        ge=1,
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level for workers",
    )


settings = WorkerSettings()
