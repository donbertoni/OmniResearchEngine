import json
import logging
from typing import Dict, Tuple

from omni.adapters.persistence.postgres.connection import get_connection

logger = logging.getLogger(__name__)


class PostgresTriggerConfigRepository:
    def save(self, org_id: str, modulo: str, config_data: dict) -> Tuple[bool, str]:
        try:
            conn = get_connection()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO trigger_configs (org_id, modulo, config, updated_at)
                            VALUES (%s, %s, %s, now())
                            ON CONFLICT (org_id, modulo) DO UPDATE
                                SET config = EXCLUDED.config, updated_at = now()
                            """,
                            (org_id, modulo, json.dumps(config_data)),
                        )
                return True, "Parâmetros e gatilhos atualizados com sucesso no Postgres!"
            finally:
                conn.close()
        except Exception as e:
            logger.error("Failed to persist trigger config to Postgres", exc_info=True)
            return False, f"Falha ao gravar configurações: {e}"

    def load(self, org_id: str, modulo: str) -> dict:
        return self.load_all(org_id).get(modulo, {})

    def load_all(self, org_id: str) -> Dict[str, dict]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT modulo, config, last_dispatched_at FROM trigger_configs WHERE org_id = %s",
                    (org_id,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        result = {}
        for modulo, config, last_dispatched_at in rows:
            data = dict(config)
            if last_dispatched_at:
                data["last_dispatched_at"] = last_dispatched_at
            result[modulo] = data
        return result

    def mark_dispatched(self, org_id: str, modulo: str, dispatched_at: str) -> None:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE trigger_configs SET last_dispatched_at = %s WHERE org_id = %s AND modulo = %s",
                        (dispatched_at, org_id, modulo),
                    )
        finally:
            conn.close()
