import pytest
from pydantic import ValidationError

from workers.config import WorkerConfig


class TestWorkerConfig:
    def test_init_with_required_fields_uses_defaults(self):
        cfg = WorkerConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
        )

        assert cfg.database_url == "postgresql+asyncpg://user:pass@localhost:5432/test"
        assert cfg.redis_url == "redis://localhost:6379/0"
        assert cfg.database_echo is False
        assert (
            cfg.bert_model_path == "assets/models/urlbert_classifier_v4/urlbert_classifier_v4.onnx"
        )
        assert cfg.bert_tokenizer_path == "assets/models/urlbert_classifier_v4"
        assert cfg.batch_size == 100
        assert cfg.classification_interval_hours == 1
        assert cfg.reclassification_sample_percent == 5.0
        assert cfg.task_soft_time_limit == 300
        assert cfg.task_time_limit == 360
        assert cfg.celery_task_max_retries == 3
        assert cfg.celery_task_retry_delay == 60
        assert cfg.log_level == "INFO"

    def test_custom_settings(self):
        cfg = WorkerConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            database_echo=True,
            bert_model_path="/custom/model.onnx",
            bert_tokenizer_path="/custom/tokenizer",
            batch_size=500,
            classification_interval_hours=6,
            reclassification_sample_percent=10.0,
            task_soft_time_limit=600,
            task_time_limit=720,
            celery_task_max_retries=5,
            celery_task_retry_delay=120,
            log_level="DEBUG",
        )

        assert cfg.database_echo is True
        assert cfg.bert_model_path == "/custom/model.onnx"
        assert cfg.bert_tokenizer_path == "/custom/tokenizer"
        assert cfg.batch_size == 500
        assert cfg.classification_interval_hours == 6
        assert cfg.reclassification_sample_percent == 10.0
        assert cfg.task_soft_time_limit == 600
        assert cfg.task_time_limit == 720
        assert cfg.celery_task_max_retries == 5
        assert cfg.celery_task_retry_delay == 120
        assert cfg.log_level == "DEBUG"

    def test_missing_required_fields(self, monkeypatch):
        # Clear env vars that might be set
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)

        with pytest.raises(ValidationError) as exc_info:
            WorkerConfig(_env_file=None, redis_url="redis://localhost:6379/0")
        assert "database_url" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            WorkerConfig(
                _env_file=None, database_url="postgresql+asyncpg://user:pass@localhost:5432/test"
            )
        assert "redis_url" in str(exc_info.value)

    def test_field_validations(self):
        base_config = {
            "database_url": "postgresql+asyncpg://user:pass@localhost:5432/test",
            "redis_url": "redis://localhost:6379/0",
        }

        with pytest.raises(ValidationError):
            WorkerConfig(**base_config, batch_size=0)

        with pytest.raises(ValidationError):
            WorkerConfig(**base_config, batch_size=1001)

        with pytest.raises(ValidationError):
            WorkerConfig(**base_config, classification_interval_hours=0)

        with pytest.raises(ValidationError):
            WorkerConfig(**base_config, classification_interval_hours=25)

        with pytest.raises(ValidationError):
            WorkerConfig(**base_config, task_soft_time_limit=59)

        with pytest.raises(ValidationError):
            WorkerConfig(**base_config, task_time_limit=59)
