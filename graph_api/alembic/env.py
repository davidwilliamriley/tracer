"""
alembic/env.py — Alembic migration environment.

Key configuration points:
  - target_metadata is set to Base.metadata so autogenerate can compare
    SQLAlchemy models against the actual database schema.
  - The database URL is read from config.settings, not alembic.ini,
    so we never have credentials in version control.
  - All models are imported via `import models` to ensure every table
    is registered with Base.metadata before autogenerate runs.
"""
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Make the project root importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from database import Base
import models  # registers all ORM models with Base.metadata

# Alembic Config object — provides access to alembic.ini values
config = context.config

# Override sqlalchemy.url with value from our settings
# This means we never need to put the DB URL in alembic.ini
config.set_main_option("sqlalchemy.url", settings.database_url)

# Set up Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# The metadata autogenerate compares against
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — generates SQL without a live connection.
    Useful for reviewing what Alembic would do before applying it.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode — connects to the database and applies changes.
    This is the normal mode used by `alembic upgrade head`.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,    # detect column type changes
            compare_server_default=True,  # detect default value changes
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
