from functools import lru_cache

from fastapi import Depends

from app.container import get_settings
from app.services.auth_service import AuthService
from core.services.hashing_service import HashingService
from infra.settings import Settings


def get_auth_service(settings: Settings = Depends(get_settings)) -> AuthService:
    return AuthService(settings)


@lru_cache
def get_hashing_service() -> HashingService:
    return HashingService()
