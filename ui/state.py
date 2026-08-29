import streamlit as st

from omni.application.agents_service import default_prediction_logs
from omni.config.settings import AppSettings
from omni.domain.catalog import CATEGORIES_CRYPTO, CATEGORIES_TRADFI, build_initial_asset_pool


def init_session_state(settings: AppSettings) -> None:
    if "custom_active_categories_crypto" not in st.session_state:
        st.session_state.custom_active_categories_crypto = CATEGORIES_CRYPTO.copy()
    if "custom_active_categories_tradfi" not in st.session_state:
        st.session_state.custom_active_categories_tradfi = CATEGORIES_TRADFI.copy()

    # Bug corrigido: o código original checava a chave "asset_pool_TradFi (Macro)"
    # mas gravava em "asset_pool_TradFi" — a checagem nunca batia, então o pool de
    # TradFi era resetado a cada rerun, descartando qualquer edição do analista.
    if "asset_pool_Crypto" not in st.session_state:
        st.session_state.asset_pool_Crypto = build_initial_asset_pool(CATEGORIES_CRYPTO)
    if "asset_pool_TradFi" not in st.session_state:
        st.session_state.asset_pool_TradFi = build_initial_asset_pool(CATEGORIES_TRADFI)

    if "config_window" not in st.session_state:
        st.session_state.config_window = None

    if "ml_prediction_logs" not in st.session_state:
        st.session_state.ml_prediction_logs = default_prediction_logs()

    # Bug corrigido: credenciais digitadas na Calibragem nunca eram persistidas em
    # session_state, então eram descartadas no rerun disparado pelo próprio submit.
    st.session_state.setdefault("brapi_token", settings.brapi_token)
    st.session_state.setdefault("custom_data_api_key", settings.custom_data_api_key)
    st.session_state.setdefault("whatsapp_instance", settings.whatsapp_instance)
    st.session_state.setdefault("whatsapp_token", settings.whatsapp_token)
