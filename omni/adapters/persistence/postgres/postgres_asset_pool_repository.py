import json
from typing import Optional

from omni.adapters.persistence.postgres.connection import get_connection


class PostgresAssetPoolRepository:
    def load_pool(self, org_id: str, modulo: str) -> Optional[list]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT pool FROM asset_pools WHERE org_id = %s AND modulo = %s", (org_id, modulo))
                row = cur.fetchone()
        finally:
            conn.close()
        if not row:
            return None
        return [tuple(item) for item in row[0]]

    def save_pool(self, org_id: str, modulo: str, pool: list) -> None:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO asset_pools (org_id, modulo, pool, updated_at) VALUES (%s, %s, %s, now())
                        ON CONFLICT (org_id, modulo) DO UPDATE SET pool = EXCLUDED.pool, updated_at = now()
                        """,
                        (org_id, modulo, json.dumps(pool)),
                    )
        finally:
            conn.close()

    def load_categories(self, org_id: str, modulo: str) -> Optional[dict]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT categories FROM asset_categories WHERE org_id = %s AND modulo = %s", (org_id, modulo))
                row = cur.fetchone()
        finally:
            conn.close()
        if not row:
            return None
        categories = dict(row[0])
        for cat_info in categories.values():
            cat_info["assets"] = [tuple(a) for a in cat_info["assets"]]
        return categories

    def save_categories(self, org_id: str, modulo: str, categories: dict) -> None:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO asset_categories (org_id, modulo, categories, updated_at) VALUES (%s, %s, %s, now())
                        ON CONFLICT (org_id, modulo) DO UPDATE SET categories = EXCLUDED.categories, updated_at = now()
                        """,
                        (org_id, modulo, json.dumps(categories)),
                    )
        finally:
            conn.close()
