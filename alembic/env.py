from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.config import get_db_url
from app.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _log_connection_info() -> str:
    url = str(get_db_url())
    user = os.getenv("POSTGRESQL_USER", "")
    host = os.getenv("POSTGRESQL_HOST", "")
    dbname = os.getenv("POSTGRESQL_DBNAME", "")
    print(f"[Alembic] ENV user={user} host={host} db={dbname}")
    parsed = make_url(url)
    password = parsed.password or ""
    safe_url = url.replace(password, "***") if password else url
    print(f"[Alembic] DSN: {safe_url}")
    return url


def run_migrations_offline() -> None:
    url = _log_connection_info()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = _log_connection_info()
    connectable = create_engine(url, future=True, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
