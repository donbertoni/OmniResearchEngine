import json
import logging
from typing import Tuple

from omni.adapters.persistence.postgres.connection import get_connection

logger = logging.getLogger(__name__)

# Nomes de tabela permitidos -- table_name nunca vem de input externo (só de
# literais nos __init__ dos subtipos abaixo), mas um allowlist explícito
# evita que isso vire um vetor de injeção por acidente numa mudança futura.
_ALLOWED_TABLES = {"automation_settings", "api_credentials"}


class SingleRowPerOrgRepository:
    """Base para repositórios Postgres que guardam um único blob JSON por
    organização (`org_id` como chave primária) -- `automation_settings` e
    `api_credentials` têm exatamente essa forma. Antes desta mudança, os dois
    repositórios duplicavam byte a byte a mesma lógica de
    conexão/cursor/INSERT..ON CONFLICT, diferindo só no nome da tabela e nas
    mensagens.
    """

    def __init__(self, table_name: str, success_message: str, error_message_prefix: str):
        if table_name not in _ALLOWED_TABLES:
            raise ValueError(f"Unknown single-row-per-org table: {table_name}")
        self._table_name = table_name
        self._success_message = success_message
        self._error_message_prefix = error_message_prefix

    def save(self, org_id: str, config_data: dict) -> Tuple[bool, str]:
        try:
            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            INSERT INTO {self._table_name} (org_id, config, updated_at)
                            VALUES (%s, %s, now())
                            ON CONFLICT (org_id) DO UPDATE
                                SET config = EXCLUDED.config, updated_at = now()
                            """,
                            (org_id, json.dumps(config_data)),
                        )
                return True, self._success_message
            finally:
                conn.close()
        except Exception as e:
            logger.error("Failed to persist %s", self._table_name, exc_info=True)
            return False, f"{self._error_message_prefix}: {e}"

    def load(self, org_id: str) -> dict:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT config FROM {self._table_name} WHERE org_id = %s", (org_id,))
                row = cur.fetchone()
        finally:
            conn.close()
        return dict(row[0]) if row else {}
