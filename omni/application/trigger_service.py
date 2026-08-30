from typing import Dict, Tuple

from omni.domain.ports import TriggerConfigRepositoryPort

MAX_TRIGGER_ASSETS = 10


def save_trigger_configuration(repo: TriggerConfigRepositoryPort, org_id: str, modulo: str, config_data: dict) -> Tuple[bool, str]:
    ativos = config_data.get("ativos_selecionados_tickers", [])
    limit = min(MAX_TRIGGER_ASSETS, config_data.get("max_free_tickers", MAX_TRIGGER_ASSETS))
    if len(ativos) > limit:
        return False, f"Erro crítico: O limite máximo é de {limit} ativos (enviados: {len(ativos)})."
    return repo.save(org_id, modulo, config_data)


def load_trigger_configuration(repo: TriggerConfigRepositoryPort, org_id: str, modulo: str) -> dict:
    return repo.load(org_id, modulo)


def load_all_trigger_configurations(repo: TriggerConfigRepositoryPort, org_id: str) -> Dict[str, dict]:
    return repo.load_all(org_id)
