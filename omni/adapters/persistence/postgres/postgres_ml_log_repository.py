from typing import List

from omni.adapters.persistence.postgres.connection import get_connection


class PostgresMlLogRepository:
    def load_all(self, org_id: str) -> List[dict]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT ts_label, asset, prediction, confidence, status FROM ml_prediction_logs "
                    "WHERE org_id = %s ORDER BY created_at DESC LIMIT 200",
                    (org_id,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return [
            {"timestamp": r[0], "asset": r[1], "prediction": r[2], "confidence": r[3], "status": r[4]}
            for r in rows
        ]

    def append(self, org_id: str, entry: dict) -> None:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO ml_prediction_logs (org_id, ts_label, asset, prediction, confidence, status) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (org_id, entry["timestamp"], entry["asset"], entry["prediction"], entry["confidence"], entry["status"]),
                    )
        finally:
            conn.close()
