from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db_session
from infra.db.repositories.urls import PostgresUrlRepository
from infra.db.repositories.users import PostgresUserRepository


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> PostgresUserRepository:
    return PostgresUserRepository(session)


def get_url_repository(session: AsyncSession = Depends(get_db_session)) -> PostgresUrlRepository:
    return PostgresUrlRepository(session)
