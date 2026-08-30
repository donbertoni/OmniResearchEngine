"""Fábrica de conexões Postgres, usada por todos os adapters em
omni/adapters/persistence/postgres/.

Deliberadamente simples (uma conexão nova por operação, sem pool) porque o
Streamlit já serializa a maior parte das interações por sessão e o volume de
escrita aqui (configs, login, pools de ativos) é baixo. Se isso virar gargalo,
trocar por um pool (ex: psycopg2.pool ou SQLAlchemy) é uma troca de adapter,
não da camada de aplicação -- é essa a vantagem de estar atrás de uma port.

O schema é gerenciado por Alembic (`alembic upgrade head`, ver migrations/ na
raiz do projeto), não mais aplicado em runtime -- o antigo
`ensure_schema()`/`schema.sql` (idempotente via `CREATE TABLE IF NOT EXISTS`)
foi removido porque não sobrevive a mudanças de schema (ex: adicionar uma
coluna a uma tabela existente), só à criação inicial.
"""

import os

import psycopg2


class PostgresNotConfiguredError(RuntimeError):
    pass


def is_configured() -> bool:
    return bool(os.environ.get("DATABASE_URL"))


def get_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise PostgresNotConfiguredError(
            "DATABASE_URL não configurada. Defina a connection string de um projeto "
            "Postgres (ex: Neon) dedicado ao OMNI -- não reaproveite o banco de outro "
            "projeto."
        )
    return psycopg2.connect(database_url)
