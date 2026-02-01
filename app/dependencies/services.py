from functools import lru_cache
from pathlib import Path

from app.container import config
from app.services.auth_service import AuthService
from core.services.classification import OnlineClassifierV1
from core.services.hashing_service import HashingService
from core.services.url_validation import UrlValidator


def get_auth_service() -> AuthService:
    return AuthService(
        token_expiration_minutes=config.access_token_expire_minutes,
        algorithm=config.algorithm,
        secret_key=config.secret_key,
    )


@lru_cache
def get_hashing_service() -> HashingService:
    return HashingService()


@lru_cache
def get_url_classifier() -> OnlineClassifierV1:
    return OnlineClassifierV1(model_path=Path(config.classifier_model_path))


@lru_cache
def get_url_validator() -> UrlValidator:
    return UrlValidator()
