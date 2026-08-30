import streamlit as st

from omni.application.agents_service import default_prediction_logs
from omni.composition import Infrastructure
from omni.domain.catalog import CATEGORIES_CRYPTO, CATEGORIES_TRADFI, build_initial_asset_pool
from omni.domain.tenancy import LEGACY_ORG_ID


def init_session_state(infra: Infrastructure) -> None:
    _init_pool_and_categories(infra, "Crypto", CATEGORIES_CRYPTO, "custom_active_categories_crypto", "asset_pool_Crypto")
    _init_pool_and_categories(infra, "TradFi (Macro)", CATEGORIES_TRADFI, "custom_active_categories_tradfi", "asset_pool_TradFi")

    if "config_window" not in st.session_state:
        st.session_state.config_window = None

    if "ml_prediction_logs" not in st.session_state:
        logs = infra.ml_log_repo.load_all(LEGACY_ORG_ID)
        st.session_state.ml_prediction_logs = logs or default_prediction_logs()

    # Credenciais: Postgres/JSON (persistente, visível ao scheduler headless)
    # tem prioridade sobre a env var, que por sua vez é só o default inicial.
    if "brapi_token" not in st.session_state:
        stored_credentials = infra.credentials_repo.load(LEGACY_ORG_ID)
        st.session_state.brapi_token = stored_credentials.get("brapi_token", infra.settings.brapi_token)
        st.session_state.whatsapp_instance = stored_credentials.get("whatsapp_instance", infra.settings.whatsapp_instance)
        st.session_state.whatsapp_token = stored_credentials.get("whatsapp_token", infra.settings.whatsapp_token)
        st.session_state.telegram_bot_token = stored_credentials.get("telegram_bot_token", infra.settings.telegram_bot_token)


def _init_pool_and_categories(infra: Infrastructure, modulo: str, default_categories: dict, categories_key: str, pool_key: str) -> None:
    if categories_key not in st.session_state:
        stored_categories = infra.asset_pool_repo.load_categories(LEGACY_ORG_ID, modulo)
        st.session_state[categories_key] = stored_categories if stored_categories is not None else default_categories.copy()

    if pool_key not in st.session_state:
        stored_pool = infra.asset_pool_repo.load_pool(LEGACY_ORG_ID, modulo)
        st.session_state[pool_key] = stored_pool if stored_pool is not None else build_initial_asset_pool(default_categories)


def persist_dirty_customizations(infra: Infrastructure) -> None:
    """As edições de pool/categorias na Calibragem só marcam um flag `*_dirty`
    em session_state (ver ui/panels/config_panels.py) -- esta função, chamada
    uma vez por rerun a partir de app.py, é quem de fato grava no repositório
    persistente, para que a customização sobreviva a um restart."""
    for modulo, categories_key, pool_key in (
        ("Crypto", "custom_active_categories_crypto", "asset_pool_Crypto"),
        ("TradFi (Macro)", "custom_active_categories_tradfi", "asset_pool_TradFi"),
    ):
        if st.session_state.pop(f"{pool_key}_dirty", False):
            infra.asset_pool_repo.save_pool(LEGACY_ORG_ID, modulo, st.session_state[pool_key])
        if st.session_state.pop(f"categories_{modulo}_dirty", False):
            infra.asset_pool_repo.save_categories(LEGACY_ORG_ID, modulo, st.session_state[categories_key])
