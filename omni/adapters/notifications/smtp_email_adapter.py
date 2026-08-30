import logging
import smtplib
from email.mime.text import MIMEText
from typing import List, Tuple

logger = logging.getLogger(__name__)


class SmtpEmailAdapter:
    """Implementa EmailPort via SMTP puro (stdlib `smtplib`, sem SaaS específico).
    Falha honesta se SMTP_HOST não estiver configurado, em vez de fingir envio."""

    def __init__(self, host: str = "", port: int = 587, user: str = "", password: str = "", from_addr: str = "", use_tls: bool = True):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._from_addr = from_addr or user
        self._use_tls = use_tls

    def send(self, to_addresses: List[str], subject: str, body: str) -> Tuple[bool, str]:
        if not to_addresses:
            return False, "Nenhum destinatário configurado."
        if not self._host:
            return False, "Integração de e-mail não configurada (defina SMTP_HOST)."

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = ", ".join(to_addresses)

        try:
            server = smtplib.SMTP(self._host, self._port, timeout=8) if self._use_tls else smtplib.SMTP_SSL(self._host, self._port, timeout=8)
            try:
                if self._use_tls:
                    server.starttls()
                if self._user:
                    server.login(self._user, self._password)
                server.sendmail(self._from_addr, to_addresses, msg.as_string())
            finally:
                server.quit()
            return True, f"E-mail enviado com sucesso para {len(to_addresses)} destinatário(s)."
        except Exception as e:
            logger.warning("SMTP dispatch failed", exc_info=True)
            return False, f"Erro ao enviar e-mail: {e}"
