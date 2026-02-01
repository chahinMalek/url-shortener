from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from workers.config import get_config
from workers.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Singleton implementation for database management logic."""

    _instance: ClassVar["DatabaseManager | None"] = None
    _engine: AsyncEngine | None = None
    _session_factory: sessionmaker | None = None

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        database_url: str | None = None,
        database_echo: bool | None = None,
    ) -> None:
        if self._engine is not None:
            logger.warning("db_engine_already_initialized")
            return

        db_url = database_url or get_config().database_url
        echo = database_echo if database_echo is not None else get_config().database_echo
        logger.info("initializing_db_engine", database_url=db_url.split("@")[-1])

        self._engine = create_async_engine(
            db_url,
            echo=echo,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self._session_factory = sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("db_engine_initialized")

    async def close(self) -> None:
        if self._engine is None:
            logger.warning("db_engine_not_initialized")
            return

        logger.info("closing_db_engine")

        await self._engine.dispose()
        self._engine = None
        self._session_factory = None

        logger.info("db_engine_closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise RuntimeError("Database engine not initialized. Call initialize() first.")

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @property
    def is_initialized(self) -> bool:
        return self._engine is not None

    def reset(self) -> None:
        self._engine = None
        self._session_factory = None
        DatabaseManager._instance = None


def get_db_manager() -> DatabaseManager:
    return DatabaseManager()


def init_db_engine() -> None:
    get_db_manager().initialize()


async def close_db_engine() -> None:
    await get_db_manager().close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_manager().get_session() as session:
        yield session
