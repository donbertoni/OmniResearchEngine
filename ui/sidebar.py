from dataclasses import dataclass

import streamlit as st

from omni.application.catalog_service import determine_tier, tier_permissions
from omni.domain.models import TierPermissions


@dataclass
class SidebarSelections:
    lang_key: str
    tr: dict
    modulo: str
    fmt_b2b: bool
    fmt_yt: bool
    fmt_wapp: bool
    fmt_tg: bool
    trigger_production: bool
    login_user: str
    tier: str
    permissions: TierPermissions


def render_sidebar(translations: dict) -> SidebarSelections:
    st.sidebar.title("🔮 OMNI Terminal")

    lang_choice = st.sidebar.selectbox("🌐 Idioma / Language", ["Português (BR)", "English (US)"], index=0)
    lang_key = "PT" if "Português" in lang_choice else "EN"
    tr = translations[lang_key]

    with st.sidebar.expander(f"👤 {tr['login']}", expanded=False):
        login_user = st.text_input(tr["user_label"], value="analista@omni.com")
        st.text_input(tr["pass_label"], value="••••••••", type="password")
        st.checkbox(tr["keep_connected"], value=True)

    tier = determine_tier(login_user)
    permissions = tier_permissions(tier)

    st.sidebar.markdown(f"**{tr['active_plan']}** `{tier}`")
    st.sidebar.markdown("---")

    modulo = st.sidebar.radio(f"⚙️ {tr['module']}", ["Crypto", "TradFi (Macro)"], index=1, key="modulo_selection")

    st.sidebar.markdown(f"### 📤 {tr['outputs']}")
    fmt_b2b = st.sidebar.checkbox(tr["fmt_b2b"], value=True)
    fmt_yt = st.sidebar.checkbox(tr["fmt_yt"], value=False)
    fmt_wapp = st.sidebar.checkbox(tr["fmt_wapp"], value=False)
    fmt_tg = st.sidebar.checkbox(tr["fmt_tg"], value=False)

    st.sidebar.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
    trigger_production = st.sidebar.button(f"🚀 {tr['production_btn']}", use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 🛠️ {tr['advanced_config']}")

    if st.sidebar.button(f"⚙️ {tr['automations']}", use_container_width=True):
        st.session_state.config_window = "automations"
    if st.sidebar.button(f"⚡ {tr['triggers']}", use_container_width=True):
        st.session_state.config_window = "triggers"
    if st.sidebar.button(f"🎛️ {tr['calibration']}", use_container_width=True):
        st.session_state.config_window = "calibration"

    return SidebarSelections(
        lang_key=lang_key,
        tr=tr,
        modulo=modulo,
        fmt_b2b=fmt_b2b,
        fmt_yt=fmt_yt,
        fmt_wapp=fmt_wapp,
        fmt_tg=fmt_tg,
        trigger_production=trigger_production,
        login_user=login_user,
        tier=tier,
        permissions=permissions,
    )
