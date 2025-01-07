"""Alembic database migration environment configuration.

This module configures and executes Alembic database migrations. It provides both offline
and online migration capabilities for the usbills.ai application.
"""

# imports
import asyncio
from logging.config import fileConfig

# packages
from alembic import context
from sqlalchemy import pool, Connection
from sqlalchemy.ext.asyncio import create_async_engine

# project
from usbills_app.config import get_config
from usbills_app.db.models.base import Base

# Alembic Config object, which provides access to the .ini file values
config = context.config

# Configure Python logging if a config file is specified
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set up target metadata for migration autogeneration support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine. By skipping the
    Engine creation we don't need a DBAPI to be available. The migration strings
    are written to script output.

    Returns:
        None
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute the migrations using the provided database connection.

    Args:
        connection: SQLAlchemy database connection object

    Returns:
        None
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an async database Engine and executes migrations within a transaction.
    This is the preferred way to run migrations in production.

    Returns:
        None
    """
    # Load application configuration
    app_config = get_config()

    # Construct database connection string
    connection_string = (
        f"{app_config.db_proto}://{app_config.db_user}:{app_config.db_password}@"
        f"{app_config.db_host}:{app_config.db_port}/{app_config.db_name}"
    )

    # Create async engine with NullPool to avoid connection pooling during migrations
    connectable = create_async_engine(
        connection_string, echo=app_config.debug, poolclass=pool.NullPool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# switch on mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
