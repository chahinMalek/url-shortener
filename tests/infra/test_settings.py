import pytest
from pydantic import ValidationError

from infra.settings import Settings


class TestSettings:
    def test_init_with_required_fields(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.database_url == "postgresql+asyncpg://user:pass@localhost:5432/test"
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.secret_key == "a" * 32

    def test_default_app_name(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.app_name == "URL Shortener"

    def test_default_debug_false(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.debug is False

    def test_default_environment(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.environment == "development"

    def test_default_database_echo_false(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.database_echo is False

    def test_default_jwt_algorithm(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.algorithm == "HS256"

    def test_default_access_token_expire_minutes(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.access_token_expire_minutes == 30

    def test_default_classifier_model_path(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
        )

        assert settings.classifier_model_path == "assets/models/online_classifier_xgb_v1.0.0.onnx"

    def test_custom_app_name(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            app_name="Custom App",
        )

        assert settings.app_name == "Custom App"

    def test_custom_debug_mode(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            debug=True,
        )

        assert settings.debug is True

    def test_custom_environment(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            environment="production",
        )

        assert settings.environment == "production"

    def test_custom_access_token_expire_minutes(self):
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
            redis_url="redis://localhost:6379/0",
            secret_key="a" * 32,
            access_token_expire_minutes=60,
        )

        assert settings.access_token_expire_minutes == 60

    def test_secret_key_min_length_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
                secret_key="short",
            )

        assert "secret_key" in str(exc_info.value)

    def test_access_token_expire_minutes_min_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
                secret_key="a" * 32,
                access_token_expire_minutes=0,
            )

        assert "access_token_expire_minutes" in str(exc_info.value)

    def test_access_token_expire_minutes_max_validation(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
                secret_key="a" * 32,
                access_token_expire_minutes=1441,
            )

        assert "access_token_expire_minutes" in str(exc_info.value)

    def test_missing_database_url(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                redis_url="redis://localhost:6379/0",
                secret_key="a" * 32,
            )

        assert "database_url" in str(exc_info.value)

    def test_missing_redis_url(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                secret_key="a" * 32,
            )

        assert "redis_url" in str(exc_info.value)

    def test_missing_secret_key(self):
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                database_url="postgresql+asyncpg://user:pass@localhost:5432/test",
                redis_url="redis://localhost:6379/0",
            )

        assert "secret_key" in str(exc_info.value)
