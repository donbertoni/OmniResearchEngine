"""Automações: antes desta mudança, os campos do painel de Automações
(e-mails, webhooks, plataforma/API key de CRM) eram só coletados em widgets do
Streamlit e nunca persistidos nem lidos de volta -- clicar em "CRM Push" apenas
mostrava um toast fixo, nenhuma requisição HTTP era feita. Agora os valores são
persistidos via AutomationConfigRepositoryPort e usados de verdade tanto pelo
botão de disparo manual quanto pelo scheduler de report automático.
"""

from dataclasses import asdict, dataclass
from typing import List, Tuple

from omni.domain.ports import AutomationConfigRepositoryPort, WebhookPort

DEFAULT_EMAILS = "mesa@gestora.com, compliance@gestora.com"


@dataclass
class AutomationSettings:
    auto_emails: str = DEFAULT_EMAILS
    auto_urls: str = ""
    crm_platform: str = "HubSpot"
    crm_api_key: str = ""
    whatsapp_numbers: str = ""
    telegram_chat_ids: str = ""


def split_targets(value: str) -> List[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def save_automation_settings(repo: AutomationConfigRepositoryPort, org_id: str, settings: AutomationSettings) -> Tuple[bool, str]:
    return repo.save(org_id, asdict(settings))


def load_automation_settings(repo: AutomationConfigRepositoryPort, org_id: str) -> AutomationSettings:
    stored = repo.load(org_id)
    defaults = asdict(AutomationSettings())
    defaults.update(stored)
    return AutomationSettings(**{k: defaults[k] for k in defaults if k in AutomationSettings.__dataclass_fields__})


def dispatch_crm_push(webhook_port: WebhookPort, settings: AutomationSettings, payload: dict) -> List[Tuple[str, bool, str]]:
    urls = split_targets(settings.auto_urls)
    if not urls:
        return [("", False, "Nenhuma URL de webhook configurada no painel de Automações.")]
    enriched_payload = {**payload, "crm_platform": settings.crm_platform}
    results = []
    for url in urls:
        ok, msg = webhook_port.post(url, enriched_payload, auth_token=settings.crm_api_key)
        results.append((url, ok, msg))
    return results
