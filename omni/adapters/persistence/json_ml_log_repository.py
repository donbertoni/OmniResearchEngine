import json
import logging
import os
from typing import List

logger = logging.getLogger(__name__)


class JsonMlLogRepository:
    """Fallback local (ver JsonTriggerConfigRepository para o porquê).
    Arquivo aninhado por `org_id`."""

    def __init__(self, logs_file: str = "ml_prediction_logs.json"):
        self._logs_file = logs_file

    def _read_all(self) -> dict:
        if os.path.exists(self._logs_file):
            try:
                with open(self._logs_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read ml prediction logs file", exc_info=True)
        return {}

    def load_all(self, org_id: str) -> List[dict]:
        return self._read_all().get(org_id, [])

    def append(self, org_id: str, entry: dict) -> None:
        all_data = self._read_all()
        logs = all_data.get(org_id, [])
        logs.insert(0, entry)
        all_data[org_id] = logs[:200]
        with open(self._logs_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
