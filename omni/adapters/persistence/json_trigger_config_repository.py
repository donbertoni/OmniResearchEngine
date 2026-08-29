import json
import logging
import os
from typing import Tuple

logger = logging.getLogger(__name__)


class JsonTriggerConfigRepository:
    def __init__(self, config_file: str = "trigger_config.json"):
        self._config_file = config_file

    def save(self, config_data: dict) -> Tuple[bool, str]:
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            return True, "Parâmetros e gatilhos atualizados com sucesso no backend!"
        except Exception as e:
            logger.error("Failed to persist trigger config", exc_info=True)
            return False, f"Falha ao gravar configurações: {e}"

    def load(self) -> dict:
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read trigger config file", exc_info=True)
        return {}
