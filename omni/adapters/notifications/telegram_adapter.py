import logging
from typing import Tuple

import requests

logger = logging.getLogger(__name__)


class TelegramNotificationAdapter:
    """Implementa NotificationPort via Telegram Bot API de verdade. Antes disso
    `build_telegram_message` era um texto estático e não existia integração
    nenhuma -- diferente do WhatsApp, que já tinha (mesmo que desconfigurado por
    padrão) um adapter real.
    """

    def send(self, target: str, message: str, credentials: dict) -> Tuple[bool, str]:
        bot_token = credentials.get("bot_token", "")
        if not target:
            return False, "Chat ID do Telegram não configurado."
        if not bot_token:
            return False, "Integração de Telegram não configurada (defina TELEGRAM_BOT_TOKEN)."
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            res = requests.post(url, json={"chat_id": target, "text": message}, timeout=6)
            if res.status_code == 200:
                return True, "Mensagem enviada com sucesso via Telegram!"
            return False, f"Falha ao enviar via Telegram (HTTP {res.status_code}): {res.text[:200]}"
        except Exception as e:
            logger.warning("Telegram dispatch failed", exc_info=True)
            return False, f"Erro ao enviar via Telegram: {e}"
