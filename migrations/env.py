"""Alembic runtime config.

Deliberately raw-SQL, no ORM models: every migration writes plain DDL via
`op.execute(...)`, matching the psycopg2-raw-SQL style already used by every
adapter under omni/adapters/persistence/postgres/. Alembic itself still
requires SQLAlchemy internally (that's fine -- it's Alembic's dependency, not
a project-wide switch to the ORM), which is why `sqlalchemy.url` still needs
to be set, just read from the same DATABASE_URL env var as everywhere else.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL não configurada -- migrations rodam contra um Postgres real, "
        "não existe fallback local em JSON para elas (ver .env.example)."
    )
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
