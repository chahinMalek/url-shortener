from functools import lru_cache
from pathlib import Path

from fastapi import Depends

from app.container import get_settings
from app.services.auth_service import AuthService
from core.services.classification import XGBUrlClassifier, create_xgb_classifier
from core.services.hashing_service import HashingService
from infra.settings import Settings


def get_auth_service(settings: Settings = Depends(get_settings)) -> AuthService:
    return AuthService(settings)


@lru_cache
def get_hashing_service() -> HashingService:
    return HashingService()


@lru_cache
def get_url_classifier(settings: Settings = Depends(get_settings)) -> XGBUrlClassifier:
    return create_xgb_classifier(
        model_path=Path(settings.classifier_model_path),
        version=settings.classifier_version,
        threshold=settings.classifier_threshold,
    )
