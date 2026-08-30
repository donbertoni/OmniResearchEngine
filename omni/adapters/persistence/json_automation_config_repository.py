import json
import logging
import os
from typing import Tuple

logger = logging.getLogger(__name__)


class JsonAutomationConfigRepository:
    """Fallback local (ver JsonTriggerConfigRepository para o porquê).
    Arquivo aninhado por `org_id`."""

    def __init__(self, config_file: str = "automation_config.json"):
        self._config_file = config_file

    def _read_all(self) -> dict:
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read automation config file", exc_info=True)
        return {}

    def save(self, org_id: str, config_data: dict) -> Tuple[bool, str]:
        try:
            all_data = self._read_all()
            all_data[org_id] = config_data
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)
            return True, "Automações salvas com sucesso!"
        except Exception as e:
            logger.error("Failed to persist automation config", exc_info=True)
            return False, f"Falha ao gravar automações: {e}"

    def load(self, org_id: str) -> dict:
        return self._read_all().get(org_id, {})
