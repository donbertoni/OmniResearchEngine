import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    brapi_token: str = ""
    custom_data_api_key: str = ""
    whatsapp_instance: str = ""
    whatsapp_token: str = ""
    whatsapp_api_base_url: str = ""


def load_settings() -> AppSettings:
    """Carrega defaults de credenciais via variáveis de ambiente.

    Isso é só o valor inicial: o analista ainda pode sobrescrever via o painel de
    Calibragem, e o valor digitado passa a ser persistido em st.session_state.
    """
    return AppSettings(
        brapi_token=os.environ.get("BRAPI_TOKEN", ""),
        custom_data_api_key=os.environ.get("CUSTOM_DATA_API_KEY", ""),
        whatsapp_instance=os.environ.get("WHATSAPP_INSTANCE_ID", ""),
        whatsapp_token=os.environ.get("WHATSAPP_TOKEN", ""),
        whatsapp_api_base_url=os.environ.get("WHATSAPP_API_BASE_URL", ""),
    )
