import pytest
from pydantic import ValidationError

from infra.config import AppConfig


class TestAppConfig:
    def test_init_with_required_fields(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.database_url == "postgresql+asyncpg://user:pass@localhost:5432/test"
        assert cfg.redis_url == "redis://localhost:6379/0"
        assert cfg.secret_key == "a" * 32

    def test_default_app_name(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.app_name == "URL Shortener"

    def test_default_debug_false(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.debug is False

    def test_default_environment(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.environment == "development"

    def test_default_database_echo_false(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.database_echo is False

    def test_default_jwt_algorithm(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.algorithm == "HS256"

    def test_default_access_token_expire_minutes(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.access_token_expire_minutes == 30

    def test_default_classifier_model_path(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert cfg.classifier_model_path == "assets/models/online_classifier_xgb_v1.0.0.onnx"

    def test_custom_app_name(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            app_name="Custom App",
        )

        assert cfg.app_name == "Custom App"

    def test_custom_debug_mode(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            debug=True,
        )

        assert cfg.debug is True

    def test_custom_environment(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            environment="production",
        )

        assert cfg.environment == "production"

    def test_custom_access_token_expire_minutes(self):
        cfg = AppConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            access_token_expire_minutes=60,
        )

        assert cfg.access_token_expire_minutes == 60

    def test_secret_key_min_length_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
                secret_key="short",
            )

        assert "secret_key" in str(exc_info.value)

    def test_access_token_expire_minutes_min_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
                secret_key="a" * 32,
                access_token_expire_minutes=0,
            )

        assert "access_token_expire_minutes" in str(exc_info.value)

    def test_access_token_expire_minutes_max_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
                secret_key="a" * 32,
                access_token_expire_minutes=1441,
            )

        assert "access_token_expire_minutes" in str(exc_info.value)

    def test_missing_database_url(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                redis_url="redis://localhost:6379/0",
                secret_key="a" * 32,
            )

        assert "database_url" in str(exc_info.value)

    def test_missing_redis_url(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                secret_key="a" * 32,
            )

        assert "redis_url" in str(exc_info.value)

    def test_missing_secret_key(self):
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
            )

        assert "secret_key" in str(exc_info.value)
