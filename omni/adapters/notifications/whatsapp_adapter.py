import logging
from typing import Tuple

import requests

logger = logging.getLogger(__name__)


class WhatsAppNotificationAdapter:
    """Implementa NotificationPort para disparo de mensagens via um gateway HTTP de
    WhatsApp (ex: Evolution API / UAZAPI-like), configurável via `base_url`.

    A versão original desta função montava o payload e os headers, nunca chamava
    `requests.post` de verdade, e ainda assim sempre retornava sucesso. Aqui o
    comportamento é honesto: se não houver `base_url` configurada (via
    WHATSAPP_API_BASE_URL), retorna falha explicando que a integração não está
    configurada, em vez de fingir que a mensagem foi enviada.
    """

    def __init__(self, base_url: str = ""):
        self._base_url = base_url.rstrip("/") if base_url else ""

    def send(self, target: str, message: str, credentials: dict) -> Tuple[bool, str]:
        instance_id = credentials.get("instance_id", "")
        token = credentials.get("token", "")

        if not target or not token:
            return False, "Credenciais de WhatsApp incompletas."
        if not self._base_url:
            return False, "Integração de WhatsApp não configurada (defina WHATSAPP_API_BASE_URL)."

        try:
            url = f"{self._base_url}/message/sendText/{instance_id}"
            headers = {"Content-Type": "application/json", "apikey": token}
            payload = {"number": target, "textMessage": {"text": message}}
            res = requests.post(url, json=payload, headers=headers, timeout=6)
            if res.status_code in (200, 201):
                return True, "Relatório disparado com sucesso via WhatsApp!"
            return False, f"Falha ao disparar WhatsApp (HTTP {res.status_code})."
        except Exception as e:
            logger.warning("WhatsApp dispatch failed", exc_info=True)
            return False, f"Erro ao disparar WhatsApp: {e}"
