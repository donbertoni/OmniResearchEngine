import logging
from typing import Tuple

import requests

logger = logging.getLogger(__name__)


class GenericWebhookAdapter:
    """Implementa WebhookPort: POST JSON genérico, usado tanto pelo botão de CRM
    Push quanto pelo scheduler de automação. Antes disso o botão "CRM Push" só
    mostrava um toast fixo e nenhuma requisição era feita de verdade."""

    def post(self, url: str, payload: dict, auth_token: str = "") -> Tuple[bool, str]:
        if not url:
            return False, "URL de webhook vazia."
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if 200 <= res.status_code < 300:
                return True, f"Payload entregue com sucesso em {url} (HTTP {res.status_code})."
            return False, f"Falha ao entregar em {url} (HTTP {res.status_code})."
        except Exception as e:
            logger.warning("Webhook dispatch failed for %s", url, exc_info=True)
            return False, f"Erro ao chamar {url}: {e}"
