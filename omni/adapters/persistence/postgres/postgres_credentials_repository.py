import json
import logging
from typing import Tuple

from omni.adapters.persistence.postgres.connection import get_connection

logger = logging.getLogger(__name__)


class PostgresCredentialsRepository:
    """Uma linha por organização (`org_id` como chave primária). Guarda
    credenciais de terceiros (BRAPI, WhatsApp, Telegram) de cada cliente --
    candidato natural a criptografia em repouso (ver docs/ARCHITECTURE.md,
    Fase 2), ainda não implementada nesta camada."""

    def save(self, org_id: str, config_data: dict) -> Tuple[bool, str]:
        try:
            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO api_credentials (org_id, config, updated_at)
                            VALUES (%s, %s, now())
                            ON CONFLICT (org_id) DO UPDATE
                                SET config = EXCLUDED.config, updated_at = now()
                            """,
                            (org_id, json.dumps(config_data)),
                        )
                return True, "Credenciais salvas com sucesso!"
            finally:
                conn.close()
        except Exception as e:
            logger.error("Failed to persist credentials", exc_info=True)
            return False, f"Falha ao gravar credenciais: {e}"

    def load(self, org_id: str) -> dict:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT config FROM api_credentials WHERE org_id = %s", (org_id,))
                row = cur.fetchone()
        finally:
            conn.close()
        return dict(row[0]) if row else {}
