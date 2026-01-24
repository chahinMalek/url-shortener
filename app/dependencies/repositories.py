from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db_session
from infra.db.repositories.classification_results import PostgresClassificationResultRepository
from infra.db.repositories.permissions import PostgresPermissionRepository
from infra.db.repositories.urls import PostgresUrlRepository
from infra.db.repositories.users import PostgresUserRepository


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> PostgresUserRepository:
    return PostgresUserRepository(session)


def get_url_repository(session: AsyncSession = Depends(get_db_session)) -> PostgresUrlRepository:
    return PostgresUrlRepository(session)


def get_permission_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresPermissionRepository:
    return PostgresPermissionRepository(session)


def get_classification_result_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresClassificationResultRepository:
    return PostgresClassificationResultRepository(session)
