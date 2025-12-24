from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db_session
from app.dependencies.repositories import get_url_repository, get_user_repository
from app.dependencies.services import get_auth_service, get_hashing_service
from core.entities.users import User
from core.services.auth_service import AuthService
from core.services.hashing_service import HashingService
from infra.db.repositories.urls import PostgresUrlRepository
from infra.db.repositories.users import PostgresUserRepository

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
UserRepoDep = Annotated[PostgresUserRepository, Depends(get_user_repository)]
UrlRepoDep = Annotated[PostgresUrlRepository, Depends(get_url_repository)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
HashingServiceDep = Annotated[HashingService, Depends(get_hashing_service)]
