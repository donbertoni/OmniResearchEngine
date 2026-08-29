from typing import Tuple

from omni.domain.ports import TriggerConfigRepositoryPort

MAX_TRIGGER_ASSETS = 10


def save_trigger_configuration(repo: TriggerConfigRepositoryPort, config_data: dict) -> Tuple[bool, str]:
    ativos = config_data.get("ativos_selecionados", [])
    if len(ativos) > MAX_TRIGGER_ASSETS:
        return False, f"Erro crítico: O limite máximo é de {MAX_TRIGGER_ASSETS} ativos (enviados: {len(ativos)})."
    return repo.save(config_data)


def load_trigger_configuration(repo: TriggerConfigRepositoryPort) -> dict:
    return repo.load()
