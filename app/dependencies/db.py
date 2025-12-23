from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.container import db_service
from infra.db.repositories.users import PostgresUserRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_service.get_session():
        yield session


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgresUserRepository:
    return PostgresUserRepository(session)
