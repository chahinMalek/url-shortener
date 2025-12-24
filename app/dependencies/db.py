from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.container import db_service


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_service.get_session():
        yield session
