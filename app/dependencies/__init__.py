from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_auth_service, get_current_user
from app.dependencies.db import get_db_session, get_user_repository
from core.entities import User
from core.services.auth_service import AuthService
from infra.db.repositories.users import PostgresUserRepository

DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
UserRepoDep = Annotated[PostgresUserRepository, Depends(get_user_repository)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


__all__ = [
    "DbSessionDep",
    "UserRepoDep",
    "AuthServiceDep",
    "CurrentUserDep",
]
