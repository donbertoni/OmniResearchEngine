from datetime import datetime

import streamlit as st

from omni.adapters.scheduling.report_scheduler import start_background_scheduler
from omni.application.dashboard_service import fetch_dashboard_snapshot
from omni.composition import build_infrastructure
from omni.domain.catalog import CRYPTO_BENCHMARKS, MACRO_BENCHMARKS
from ui import state, styles
from ui.panels.agents_panel import render_agents_panel
from ui.panels.category_panel import render_category_panel
from ui.panels.config_panels import render_config_window
from ui.panels.cycle_panel import render_cycle_panel
from ui.panels.deliveries_panel import render_deliveries_panel
from ui.panels.heatmap_panel import render_heatmap_panel
from ui.panels.metrics_panel import render_metrics_panel
from ui.sidebar import render_sidebar
from ui.translations import TRANSLATIONS

# Composition root real: omni/composition.py monta todos os adapters concretos
# (Postgres se DATABASE_URL estiver configurada, fallback local em JSON caso
# contrário) usados tanto aqui quanto em scheduler_worker.py.
_infra = build_infrastructure()
start_background_scheduler(_infra)


@st.cache_data(ttl=60, show_spinner=False)
def _cached_dashboard_snapshot(symbols: tuple, brapi_token: str):
    # Bug corrigido: antes nenhuma das chamadas de API tinha cache, então cada
    # interação (marcar checkbox, trocar de aba) refazia todas as requisições
    # externas, e o botão "Refresh" (que só chamava st.cache_data.clear()) não
    # tinha efeito nenhum porque não havia nada cacheado para limpar.
    return fetch_dashboard_snapshot(_infra.market_data_port, _infra.sentiment_port, _infra.global_market_port, symbols, brapi_token)


def run() -> None:
    st.set_page_config(page_title="OMNIRESEARCH Engine", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
    styles.inject(st)

    state.init_session_state(_infra)

    selections = render_sidebar(TRANSLATIONS, _infra.user_repo)
    tr = selections.tr
    lang_key = selections.lang_key
    modulo = selections.modulo
    permissions = selections.permissions

    if not _infra.using_postgres:
        st.markdown(
            '<div class="warning-bar">⚠️ DATABASE_URL não configurada -- login, gatilhos, automações e pools de '
            "ativos estão em arquivos JSON locais e NÃO sobrevivem a um redeploy. Configure um Postgres dedicado "
            "(ver .env.example).</div>",
            unsafe_allow_html=True,
        )

    if modulo == "Crypto":
        active_categories = st.session_state.custom_active_categories_crypto
        current_asset_pool = st.session_state.asset_pool_Crypto
        pool_state_key = "asset_pool_Crypto"
    else:
        active_categories = st.session_state.custom_active_categories_tradfi
        current_asset_pool = st.session_state.asset_pool_TradFi
        pool_state_key = "asset_pool_TradFi"

    active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

    company_name = "OMNIRESEARCH Engine"
    cnpi_code = "CNPI-T 0000"
    if permissions.allow_white_label:
        company_name = "XP / BTG / Gestora"
        cnpi_code = "CNPI-T 3421"

    if permissions.allow_white_label and company_name != "OMNIRESEARCH Engine":
        st.title(f"🏛️ {company_name} — Terminal Quant")
        st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
    else:
        st.title("⚡ OMNIRESEARCH Engine")
        st.caption("Plataforma Integrada de Inteligência Financeira com IA & Auto-Pilot (Bilingual Ready)")

    automation_settings = render_config_window(
        tr, modulo, active_categories, current_asset_pool, pool_state_key,
        permissions, _infra.trigger_repo, _infra.automation_repo, _infra.credentials_repo,
    )
    state.persist_dirty_customizations(_infra)

    now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT" if lang_key == "PT" else "%Y-%m-%d at %H:%M:%S UTC")
    is_weekend = datetime.now().weekday() >= 5
    sources_str = "BRAPI / Yahoo" if modulo == "TradFi (Macro)" else "BRAPI / Yahoo / Deribit"

    now_time = datetime.now()
    next_report_hour = (now_time.hour // 3 + 1) * 3
    if next_report_hour >= 24:
        next_report_hour = 3
    mins_left = (next_report_hour - now_time.hour - 1) * 60 + (60 - now_time.minute)
    hrs_left = mins_left // 60
    m_left = mins_left % 60
    countdown_text = f"{hrs_left}h {m_left:02d}m" if hrs_left > 0 else f"{m_left}m"

    col_status, col_health, col_btn_refresh = st.columns([2.3, 1.8, 0.9])
    with col_status:
        st.markdown(f'<div class="status-bar">🕒 <b>{now_str[:10]}</b> | Source: {sources_str}</div>', unsafe_allow_html=True)
    with col_health:
        st.markdown(
            f'<div class="status-bar" style="border-color: #238636; justify-content: space-between;">'
            f'<span>🟢 <b>Auto-Pilot</b></span><span style="font-size: 12px; color: #8B949E;">'
            f'Next: <b style="color: #3FB950;">{countdown_text}</b></span></div>',
            unsafe_allow_html=True,
        )
    with col_btn_refresh:
        if st.button(tr["refresh_btn"], use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if modulo == "TradFi (Macro)" and is_weekend:
        st.markdown(f'<div class="warning-bar" style="margin-top: 8px;">{tr["weekend_msg"]}</div>', unsafe_allow_html=True)

    symbols_to_fetch = [item["ticker"] for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS if item.get("ticker")]
    for cat_info in active_categories.values():
        for _, ticker, _ in cat_info["assets"]:
            symbols_to_fetch.append(ticker)

    snapshot = _cached_dashboard_snapshot(tuple(dict.fromkeys(symbols_to_fetch)), st.session_state.get("brapi_token", ""))
    quotes = snapshot.quotes
    sentiment = snapshot.sentiment
    global_stats = snapshot.global_stats

    if snapshot.warnings:
        with st.expander(f"⚠️ {len(snapshot.warnings)} fonte(s) de dado indisponível(is) -- exibindo fallback", expanded=False):
            for warning in snapshot.warnings:
                st.warning(warning)

    active_display_categories = active_categories.copy()

    whatsapp_credentials = {
        "instance_id": st.session_state.get("whatsapp_instance", ""),
        "token": st.session_state.get("whatsapp_token", ""),
    }
    telegram_credentials = {"bot_token": st.session_state.get("telegram_bot_token", "")}

    col_left, col_right = st.columns([1.3, 1])
    with col_left:
        render_deliveries_panel(
            tr, modulo, lang_key, now_str, company_name, cnpi_code, sentiment,
            active_display_categories, quotes,
            selections.fmt_b2b, selections.fmt_yt, selections.fmt_wapp, selections.fmt_tg,
            automation_settings, _infra.pdf_exporter_port,
            _infra.webhook_port, _infra.email_port, _infra.whatsapp_port, _infra.telegram_port,
            whatsapp_credentials, telegram_credentials,
        )
    with col_right:
        render_metrics_panel(tr, modulo, active_benchmarks, quotes, sentiment, global_stats)

    st.markdown("---")
    render_category_panel(tr, modulo, active_display_categories, quotes)

    st.markdown("---")
    render_agents_panel(tr, lang_key, quotes, _infra.ml_log_repo)

    st.markdown("---")
    render_heatmap_panel(tr, modulo, lang_key, quotes, _infra.crypto_liquidity_port, _infra.tradfi_liquidity_port)

    if modulo == "Crypto":
        st.markdown("---")
        render_cycle_panel()

    st.markdown("---")
    st.caption("©️ Powered by OMNIRESEARCH Engine — Predictive Financial Intelligence & Autonomous Agents.")
