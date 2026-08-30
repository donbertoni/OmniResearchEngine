import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    brapi_token: str = ""
    whatsapp_instance: str = ""
    whatsapp_token: str = ""
    whatsapp_api_base_url: str = ""
    telegram_bot_token: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True


def load_settings() -> AppSettings:
    """Carrega defaults de credenciais via variáveis de ambiente.

    Isso é só o valor inicial: o analista ainda pode sobrescrever via o painel de
    Calibragem, e o valor digitado passa a ser persistido via
    CredentialsRepositoryPort (Postgres, ou o fallback local em JSON) -- não só
    em st.session_state, para que o scheduler de Auto-Pilot (que não tem uma
    sessão de navegador ativa) também enxergue as credenciais mais recentes.
    """
    return AppSettings(
        brapi_token=os.environ.get("BRAPI_TOKEN", ""),
        whatsapp_instance=os.environ.get("WHATSAPP_INSTANCE_ID", ""),
        whatsapp_token=os.environ.get("WHATSAPP_TOKEN", ""),
        whatsapp_api_base_url=os.environ.get("WHATSAPP_API_BASE_URL", ""),
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        smtp_host=os.environ.get("SMTP_HOST", ""),
        smtp_port=int(os.environ.get("SMTP_PORT", "587")),
        smtp_user=os.environ.get("SMTP_USER", ""),
        smtp_password=os.environ.get("SMTP_PASSWORD", ""),
        smtp_from=os.environ.get("SMTP_FROM", ""),
        smtp_use_tls=os.environ.get("SMTP_USE_TLS", "true").lower() != "false",
    )
