import json
import logging
import os
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class JsonTriggerConfigRepository:
    """Fallback local usado quando DATABASE_URL não está configurada.

    Estado não sobrevive a um deploy sem disco persistente (ex: a maioria dos
    PaaS de container efêmero) -- por isso o Postgres é a opção recomendada em
    produção (ver omni/adapters/persistence/postgres/). Mantido por ser simples
    para rodar localmente sem nenhuma infra externa.

    Arquivo aninhado por `org_id` (`{org_id: {modulo: config}}`) -- não há
    isolamento real entre "tenants" nesse fallback (é um único arquivo local,
    de uso single-usuário por natureza), só o mesmo formato de chamada que o
    adapter Postgres usa.
    """

    def __init__(self, config_file: str = "trigger_config.json"):
        self._config_file = config_file

    def _read_all(self) -> dict:
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read trigger config file", exc_info=True)
        return {}

    def _write_all(self, data: dict) -> None:
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save(self, org_id: str, modulo: str, config_data: dict) -> Tuple[bool, str]:
        try:
            all_data = self._read_all()
            all_data.setdefault(org_id, {})[modulo] = config_data
            self._write_all(all_data)
            return True, "Parâmetros e gatilhos atualizados com sucesso no backend!"
        except Exception as e:
            logger.error("Failed to persist trigger config", exc_info=True)
            return False, f"Falha ao gravar configurações: {e}"

    def load(self, org_id: str, modulo: str) -> dict:
        return self._read_all().get(org_id, {}).get(modulo, {})

    def load_all(self, org_id: str) -> Dict[str, dict]:
        return self._read_all().get(org_id, {})

    def mark_dispatched(self, org_id: str, modulo: str, dispatched_at: str) -> None:
        all_data = self._read_all()
        if modulo in all_data.get(org_id, {}):
            all_data[org_id][modulo]["last_dispatched_at"] = dispatched_at
            self._write_all(all_data)
