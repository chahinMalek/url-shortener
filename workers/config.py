from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery broker and result backend",
    )

    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL async connection string (required)",
    )

    BERT_MODEL_PATH: str = Field(
        default="assets/models/urlbert_classifier_v4/model.onnx",
        description="Path to ONNX model file",
    )
    BERT_TOKENIZER_PATH: str = Field(
        default="assets/models/urlbert_classifier_v4",
        description="Path to tokenizer directory",
    )

    BATCH_SIZE: int = Field(
        default=100,
        description="Number of URLs to process per task execution",
        ge=1,
        le=1000,
    )

    CLASSIFICATION_INTERVAL_MINUTES: int = Field(
        default=60,
        description="Interval between classification runs (in minutes)",
        ge=1,
        le=1440,
    )

    RECLASSIFICATION_SAMPLE_PERCENT: float = Field(
        default=5.0,
        description="Percentage of non-PENDING URLs to re-classify",
        ge=0.1,
        le=100.0,
    )

    TASK_SOFT_TIME_LIMIT: int = Field(
        default=300,
        description="Soft time limit for tasks in seconds (raises exception)",
        ge=60,
    )
    TASK_TIME_LIMIT: int = Field(
        default=360,
        description="Hard time limit for tasks in seconds (kills task)",
        ge=60,
    )

    CELERY_TASK_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of retries for failed tasks",
        ge=0,
        le=10,
    )
    CELERY_TASK_RETRY_DELAY: int = Field(
        default=60,
        description="Delay between retries in seconds",
        ge=1,
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level for workers",
    )


settings = WorkerSettings()
