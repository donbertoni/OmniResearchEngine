from dataclasses import dataclass
from typing import Optional

import streamlit as st

from omni.application import auth_service, catalog_service, session_token_service
from omni.domain.models import TierPermissions, User
from omni.domain.ports import UserRepositoryPort


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
    user: Optional[User]
    tier: str
    permissions: TierPermissions


def _try_auto_login_from_query_param(user_repo: UserRepositoryPort) -> None:
    if st.session_state.get("auth_user") is not None:
        return
    token = st.query_params.get("session")
    if not token:
        return
    email = session_token_service.verify_token(token)
    if email:
        user = user_repo.get_by_email(email)
        if user:
            st.session_state.auth_user = user


def _render_login_box(tr: dict, user_repo: UserRepositoryPort) -> None:
    user: Optional[User] = st.session_state.get("auth_user")

    if user:
        st.write(f"✅ **{user.email}**")
        if st.button(tr["logout_btn"], use_container_width=True):
            st.session_state.auth_user = None
            st.query_params.clear()
            st.rerun()
        return

    mode = st.session_state.get("auth_mode", "login")
    tab_login, tab_signup = st.tabs([tr["login_btn"], tr["create_account_btn"]])

    with tab_login:
        email = st.text_input(tr["user_label"], value="", key="login_email")
        password = st.text_input(tr["pass_label"], value="", type="password", key="login_password")
        keep_connected = st.checkbox(tr["keep_connected"], value=True, key="login_keep_connected")
        if st.button(tr["login_btn"], use_container_width=True, key="login_submit"):
            authenticated_user, msg = auth_service.authenticate(user_repo, email, password)
            if authenticated_user:
                st.session_state.auth_user = authenticated_user
                if keep_connected:
                    st.query_params["session"] = session_token_service.create_token(authenticated_user.email)
                st.rerun()
            else:
                st.error(msg)

    with tab_signup:
        new_email = st.text_input(tr["user_label"], value="", key="signup_email")
        new_password = st.text_input(tr["pass_label"], value="", type="password", key="signup_password")
        if st.button(tr["create_account_btn"], use_container_width=True, key="signup_submit"):
            ok, msg = auth_service.register(user_repo, new_email, new_password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def render_sidebar(translations: dict, user_repo: UserRepositoryPort) -> SidebarSelections:
    st.sidebar.title("🔮 OMNI Terminal")

    lang_choice = st.sidebar.selectbox("🌐 Idioma / Language", ["Português (BR)", "English (US)"], index=0)
    lang_key = "PT" if "Português" in lang_choice else "EN"
    tr = translations[lang_key]

    _try_auto_login_from_query_param(user_repo)

    with st.sidebar.expander(f"👤 {tr['login']}", expanded=st.session_state.get("auth_user") is None):
        _render_login_box(tr, user_repo)

    user: Optional[User] = st.session_state.get("auth_user")
    tier = user.tier if user else "Free (Lead Magnet)"
    permissions = catalog_service.tier_permissions(tier)

    st.sidebar.markdown(f"**{tr['active_plan']}** `{tier}`" + ("" if user else f" ({tr['login_required_hint']})"))
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
        user=user,
        tier=tier,
        permissions=permissions,
    )
