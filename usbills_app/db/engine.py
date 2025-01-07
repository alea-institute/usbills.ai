"""
Database engine module
"""

# imports
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

# packages
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

# project
from usbills_app.config import AppConfig, get_config
from usbills_app.logger import create_logger

# set up logger
LOGGER = create_logger(__name__)


def get_asyncpg_engine(
    app_config: Optional[AppConfig] = None,
) -> AsyncEngine:
    """
    Get an asyncpg engine using the app configuration.

    Args:
        app_config (Optional[AppConfig]): The app configuration to use. If None, load from file.

    Returns:
        AsyncEngine: The asyncpg engine.
    """
    if app_config is None:
        app_config = get_config()

    connection_string = (
        f"{app_config.db_proto}://{app_config.db_user}:{app_config.db_password}@"
        f"{app_config.db_host}:{app_config.db_port}/{app_config.db_name}"
    )

    engine = create_async_engine(
        connection_string,
        isolation_level="AUTOCOMMIT",
        max_overflow=0,
        pool_size=app_config.db_pool_size,
        pool_reset_on_return="commit",
        pool_pre_ping=True,
        pool_timeout=1,
        query_cache_size=0,
        echo=True if app_config.log_level == "DEBUG" else False,
        echo_pool=True if app_config.log_level == "DEBUG" else False,
    )

    # log it
    LOGGER.info("Created asyncpg engine with connection string: %s", connection_string)

    return engine


def get_sync_engine(
    app_config: Optional[AppConfig] = None,
) -> Engine:
    """
    Get a sync engine using the app configuration.

    Args:
        app_config (Optional[AppConfig]): The app configuration to use. If None, load from file.

    Returns:
        Engine: The sync engine.
    """
    if app_config is None:
        app_config = get_config()

    # Switch to psycopg2 for sync connections
    db_proto = app_config.db_proto.replace("+asyncpg", "")

    connection_string = (
        f"{db_proto}://{app_config.db_user}:{app_config.db_password}@"
        f"{app_config.db_host}:{app_config.db_port}/{app_config.db_name}"
    )

    engine = create_engine(
        connection_string,
        isolation_level="REPEATABLE READ",
        max_overflow=0,
        pool_size=app_config.db_pool_size,
        pool_reset_on_return="commit",
        pool_pre_ping=True,
        pool_timeout=1,
        query_cache_size=0,
        echo=app_config.debug,
        echo_pool=app_config.debug,
    )

    # log it
    LOGGER.info("Created sync engine with connection string: %s", connection_string)

    return engine


# create the module level async and sync engine
async_engine = get_asyncpg_engine()

# create the async session factory
async_session_factory = sessionmaker(
    async_engine, expire_on_commit=False, autoflush=True, class_=AsyncSession
)


async def get_async_session(
    conn: Optional[AsyncEngine] = None,
) -> AsyncSession:
    """
    Get an async session.

    Note that the user is responsible for closing the session.

    Args:
        conn (Optional[AsyncEngine]): The async engine to use. If None, use the module level engine.

    Returns:
        AsyncSession: The async session.
    """
    if conn is not None:
        factory = sessionmaker(
            conn,
            expire_on_commit=False,
            autoflush=True,
            class_=AsyncSession,
        )
        return factory()

    return async_session_factory()


async def get_async_session_generator(
    conn: Optional[AsyncEngine] = None,
    commit: bool = True,
    close: bool = True,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async session generator that handles commits and closes.

    Args:
        conn (Optional[AsyncEngine]): The async engine to use. If None, use the module level engine.
        commit (bool): Whether to commit the session on exit.
        close (bool): Whether to close the session on exit.

    Returns:
        AsyncGenerator[AsyncSession]: The async session generator.
    """
    if conn is not None:
        factory = sessionmaker(
            conn, expire_on_commit=False, autoflush=True, class_=AsyncSession
        )
    else:
        factory = async_session_factory

    async with factory() as session:
        try:
            LOGGER.info("Starting async session generator")
            yield session
            if commit:
                LOGGER.info("Committing session")
                await session.commit()
        except Exception as session_error:
            LOGGER.error(
                "Error in async session generator: %s", session_error, exc_info=True
            )
            await session.rollback()
            raise session_error
        finally:
            if close:
                LOGGER.info("Closing session")
                await session.close()


@asynccontextmanager
async def managed_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    A context manager that yields an AsyncSession and ensures it's closed properly.
    """
    session = await get_async_session()
    try:
        yield session
    finally:
        await session.close()


async def async_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an AsyncSession.
    """
    async with managed_async_session() as session:
        yield session
