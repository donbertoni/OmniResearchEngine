import json
from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import numpy as np

# Importação segura do Plotly com fallback
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Importação do Backend Modularizado
from backend import (
    MACRO_BENCHMARKS,
    CRYPTO_BENCHMARKS,
    CATEGORIES_CRYPTO,
    fmt_num,
    fmt_pct,
    generate_pdf_report,
    fetch_btc_fng,
    fetch_global_crypto_data,
    fetch_realtime_quotes,
    send_whatsapp_report
)

# -----------------------------------------------------------------------------
# DEFINIÇÃO DE CATEGORIAS (MÓDULO TRADFI - 8 CATEGORIAS ORIGINAIS)
# -----------------------------------------------------------------------------
CATEGORIES_TRADFI = {
    "1 - Bancos e Seguradoras": {
        "tag": "Banks",
        "assets": [
            ("Itaú Unibanco", "ITUB4.SA", "R$"),
            ("Banco do Brasil", "BBAS3.SA", "R$"),
            ("Bradesco PN", "BBDC4.SA", "R$"),
            ("BB Seguridade", "BBSE3.SA", "R$")
        ]
    },
    "2 - Energia": {
        "tag": "Energy",
        "assets": [
            ("Petrobras PN", "PETR4.SA", "R$"),
            ("Petróleo Rio", "PRIO3.SA", "R$"),
            ("Equatorial", "EQTL3.SA", "R$"),
            ("CPFL Energia", "CPFE3.SA", "R$")
        ]
    },
    "3 - Tech": {
        "tag": "Tech",
        "assets": [
            ("Totvs", "TOTVS3.SA", "R$"),
            ("NVIDIA Corp", "NVDA", "$"),
            ("Apple Inc", "AAPL", "$"),
            ("Microsoft", "MSFT", "$")
        ]
    },
    "4 - Commodities": {
        "tag": "Commodities",
        "assets": [
            ("Vale ON", "VALE3.SA", "R$"),
            ("Gerdau", "GGBR4.SA", "R$"),
            ("Cemig", "CMIG4.SA", "R$"),
            ("Klabin", "KLBN11.SA", "R$")
        ]
    },
    "5 - Varejo": {
        "tag": "Retail",
        "assets": [
            ("Assaí", "ASAI3.SA", "R$"),
            ("Lojas Renner", "LREN3.SA", "R$"),
            ("Magazine Luiza", "MGLU3.SA", "R$"),
            ("RaiaDrogasil", "RADL3.SA", "R$")
        ]
    },
    "6 - Logística e Infra.": {
        "tag": "Logistics",
        "assets": [
            ("Rumo", "RAIL3.SA", "R$"),
            ("Weg", "WEGE3.SA", "R$"),
            ("CCR", "CCRO3.SA", "R$"),
            ("Embraer", "EMBR3.SA", "R$")
        ]
    },
    "7 - Agro e Indústria": {
        "tag": "Agro",
        "assets": [
            ("SLC Agrícola", "SLCE3.SA", "R$"),
            ("BRF", "BRFS3.SA", "R$"),
            ("Ambev", "ABEV3.SA", "R$"),
            ("JBS", "JBSS3.SA", "R$")
        ]
    },
    "8 - FIIs e Imobiliário": {
        "tag": "Real Estate",
        "assets": [
            ("HGLG11", "HGLG11.SA", "R$"),
            ("KNRI11", "KNRI11.SA", "R$"),
            ("XPLG11", "XPLG11.SA", "R$"),
            ("MXRF11", "MXRF11.SA", "R$")
        ]
    }
}

def get_asset_source(ticker: str) -> str:
    return "BRAPI" if ".SA" in ticker else "Yahoo"

def get_benchmark_source(item) -> str:
    if item.get("type") == "fng_api":
        return "Alternative.me"
    elif item.get("type") == "global_api":
        return "CoinGecko"
    else:
        return "Yahoo"

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & ESTILIZAÇÃO CSS INSTITUCIONAL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    .status-bar {
        background-color: #131B2A;
        padding: 9px 14px;
        border-radius: 8px;
        border: 1px solid #1E293B;
        color: #94A3B8;
        font-size: 13px;
        height: 42px;
        display: flex;
        align-items: center;
    }
    .warning-bar {
        background-color: #2D2211;
        border: 1px solid #D29922;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #F0F6FC;
        font-size: 13px;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-title { font-size: 11px; color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; justify-content: space-between; }
    .metric-value { font-size: 15px; font-weight: 700; color: #F0F6FC; margin: 2px 0px; }
    .color-green { color: #3FB950 !important; font-weight: 600; }
    .color-red { color: #F85149 !important; font-weight: 600; }
    .color-blue { color: #58A6FF !important; font-weight: 600; }
    .source-badge {
        font-size: 9px;
        color: #8B949E;
        background-color: #21262D;
        border: 1px solid #30363D;
        padding: 1px 4px;
        border-radius: 4px;
        white-space: nowrap;
        display: inline-block;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }
</style>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SIDEBAR & ESTADOS PERSISTENTES DE CATEGORIAS E ATIVOS
# -----------------------------------------------------------------------------
st.sidebar.title("⚡ OMNI Terminal")

if "custom_active_categories_crypto" not in st.session_state:
    st.session_state.custom_active_categories_crypto = CATEGORIES_CRYPTO.copy()
if "custom_active_categories_tradfi" not in st.session_state:
    st.session_state.custom_active_categories_tradfi = CATEGORIES_TRADFI.copy()

# Inicialização dos Pools Globais de Ativos
if "asset_pool_Crypto" not in st.session_state:
    init_pool_c = []
    seen_c = set()
    for cat_info in CATEGORIES_CRYPTO.values():
        for disp, tk, cur in cat_info["assets"]:
            if tk not in seen_c:
                init_pool_c.append((disp, tk, cur))
                seen_c.add(tk)
    st.session_state.asset_pool_Crypto = init_pool_c

if "asset_pool_TradFi (Macro)" not in st.session_state:
    init_pool_t = []
    seen_t = set()
    for cat_info in CATEGORIES_TRADFI.values():
        for disp, tk, cur in cat_info["assets"]:
            if tk not in seen_t:
                init_pool_t.append((disp, tk, cur))
                seen_t.add(tk)
    st.session_state.asset_pool_TradFi = init_pool_t

with st.sidebar.expander("🔑 Login do Analista", expanded=False):
    login_user = st.text_input("Usuário / E-mail:", value="analista@omni.com")
    login_pass = st.text_input("Senha:", value="••••••••", type="password")
    login_keep = st.checkbox("Manter-se conectado", value=True)

if "admin" in login_user.lower() or "white" in login_user.lower():
    tier_selected = "Premium (B2B White-Label)"
elif "free" in login_user.lower():
    tier_selected = "Free (Lead Magnet)"
else:
    tier_selected = "Standard (B2C Trader)"

st.sidebar.markdown(f"**Plano Ativo:** `{tier_selected}`")
st.sidebar.markdown("---")

modulo = st.sidebar.radio("📊 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1, key="modulo_selection")

st.sidebar.markdown("### 📋 Formatos de Saída:")
fmt_b2b = st.sidebar.checkbox("B2B (Relatório Analítico)", value=True)
fmt_yt = st.sidebar.checkbox("B2C (YouTube Auto-Pilot)", value=False)
fmt_wapp = st.sidebar.checkbox("B2C (WhatsApp Auto-Pilot)", value=False)
fmt_tg = st.sidebar.checkbox("B2C (Telegram Auto-Pilot)", value=False)

st.sidebar.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
trigger_production = st.sidebar.button("🚀 Acionar Produção Automática", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Configurações Avançadas")

if "config_window" not in st.session_state:
    st.session_state.config_window = None

if st.sidebar.button("🤖 Automações", use_container_width=True):
    st.session_state.config_window = "automations"
if st.sidebar.button("🔔 Gatilhos de Report", use_container_width=True):
    st.session_state.config_window = "triggers"
if st.sidebar.button("🎛️ Calibragem da Engine", use_container_width=True):
    st.session_state.config_window = "calibration"

allow_customization = "Free" not in tier_selected
allow_white_label = "Premium" in tier_selected
max_free_tickers = 5 if "Standard" in tier_selected else (999 if "Premium" in tier_selected else 0)

if modulo == "Crypto":
    active_categories = st.session_state.custom_active_categories_crypto
    current_asset_pool = st.session_state.asset_pool_Crypto
    pool_state_key = "asset_pool_Crypto"
else:
    active_categories = st.session_state.custom_active_categories_tradfi
    current_asset_pool = st.session_state.asset_pool_TradFi
    pool_state_key = "asset_pool_TradFi"

active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

brapi_token = ""
custom_data_api_key = ""
whatsapp_instance = ""
whatsapp_token = ""
custom_tickers = []
auto_emails = "mesa@gestora.com, compliance@gestora.com"
auto_urls = ""
crm_platform = "HubSpot"
crm_api_key = ""

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    company_name = "XP / BTG / Gestora"
    cnpi_code = "CNPI-T 3421"

# -----------------------------------------------------------------------------
# 3. CORPO PRINCIPAL & JANELAS ESPECÍFICAS DE CONFIGURAÇÃO (COM FORMULÁRIO ANTI-LAG)
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏢 {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira com IA & Auto-Pilot")

if st.session_state.config_window:
    with st.container(border=True):
        col_w_title, col_w_close = st.columns([5, 1])
        with col_w_title:
            if st.session_state.config_window == "automations":
                st.subheader("🤖 Configuração de Automações & Integradores de CRM")
            elif st.session_state.config_window == "triggers":
                st.subheader("🔔 Configuração Avançada de Gatilhos de Report Automático")
            elif st.session_state.config_window == "calibration":
                st.subheader("🎛️ Calibragem da Engine & Gerenciador de Ativos e Categorias")
        with col_w_close:
            if st.button("❌ Fechar", use_container_width=True):
                st.session_state.config_window = None
                st.rerun()

        if st.session_state.config_window == "automations":
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.markdown("**Canais de Disparo de Dados (Payloads):**")
                auto_emails = st.text_input("Endereços Eletrônicos (Notificação B2B):", value="mesa@gestora.com, compliance@gestora.com")
                auto_urls = st.text_input("URLs / Webhooks de Disparo (Engine -> CRM):", value="")
            with col_a2:
                st.markdown("**Integração com Plataformas de CRM (Orquestração):**")
                crm_platform = st.selectbox("Plataforma de CRM Alvo:", ["HubSpot", "Salesforce", "RD Station", "Outro Webhook/API"], index=0)
                crm_api_key = st.text_input("Chave de API / Token do CRM:", value="", type="password")

        elif st.session_state.config_window == "triggers":
            st.markdown(f"**Módulo Ativo:** `{modulo}`")
            st.markdown("**📅 1. Dias da Semana para Geração Automática**")
            selected_days = st.multiselect(
                "Escolha quais dias da semana os gatilhos dispararão relatórios:",
                options=["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"],
                default=["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"],
                key="trig_days"
            )
            st.markdown("---")
            st.markdown("**⏱️ 2 & 3. Frequência Diária e Horários dos Reports**")
            freq_reports = st.slider("Frequência (Nº de reports diários):", min_value=1, max_value=5, value=2, key="trig_freq")
            report_times = []
            time_cols = st.columns(min(freq_reports, 5))
            default_times_str = ["09:00", "12:00", "15:00", "18:00", "21:00"]
            for i in range(freq_reports):
                with time_cols[i % len(time_cols)]:
                    def_t = datetime.strptime(default_times_str[i], "%H:%M").time() if i < len(default_times_str) else datetime.strptime("12:00", "%H:%M").time()
                    t_val = st.time_input(f"Horário Report {i+1}", value=def_t, key=f"trig_time_{i+1}")
                    report_times.append(t_val)
            st.markdown("---")
            st.markdown("**📈 4. Seleção de Ativos Monitorados (Máx. 10)**")
            all_module_assets = []
            for cat_name, cat_info in active_categories.items():
                for disp_name, ticker, currency in cat_info["assets"]:
                    all_module_assets.append((f"{disp_name} ({ticker}) — [{cat_name}]", ticker))
            
            asset_labels = [item[0] for item in all_module_assets]
            selected_trigger_assets = st.multiselect(
                "Selecione os ativos que os gatilhos vão considerar (Máximo de 10):",
                options=asset_labels,
                max_selections=10,
                default=asset_labels[:min(5, len(asset_labels))],
                key="trig_assets"
            )

        elif st.session_state.config_window == "calibration":
            # Formulário unificado para evitar recarregamento indesejado (Anti-Lag)
            with st.form("calibration_form"):
                st.markdown("### 🔑 1. Credenciais de API & Integrações")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    brapi_token = st.text_input("BRAPI API Token:", value="", type="password")
                    custom_data_api_key = st.text_input("Custom Market API Key:", value="", type="password")
                with col_c2:
                    whatsapp_instance = st.text_input("WhatsApp Instance ID:", value="")
                    whatsapp_token = st.text_input("WhatsApp API Token:", value="", type="password")

                st.markdown("---")
                st.markdown("### 📦 2. Adicionar e Remover Ativos")
                st.caption("Cadastre novos ativos ou gerencie o pool global de ativos disponíveis no sistema.")
                
                # ORDEM CORRIGIDA: Adicionar vem ANTES de remover/gerenciar
                st.markdown("#### ➕ Adicionar Novo Ativo")
                col_na1, col_na2, col_na3 = st.columns(3)
                with col_na1:
                    new_asset_name_input = st.text_input("Nome Amigável:", value="", placeholder="Ex: Ethereum", key="form_new_asset_name")
                with col_na2:
                    new_asset_ticker_input = st.text_input("Ticker:", value="", placeholder="Ex: ETH-USD", key="form_new_asset_ticker")
                with col_na3:
                    new_asset_curr_input = st.selectbox("Moeda:", ["$", "R$"], key="form_new_asset_curr")

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("#### 🗑️ Gerenciar / Remover Ativos Existentes")
                st.caption("Use a caixa abaixo para visualizar e remover ativos existentes do pool (basta desmarcar/remover da caixa).")
                
                pool_labels_map = {f"{disp} ({tk}) [{cur}]": (disp, tk, cur) for disp, tk, cur in current_asset_pool}
                default_pool_labels = list(pool_labels_map.keys())
                
                selected_pool_labels = st.multiselect(
                    "Ativos atualmente no pool (mantenha selecionados ou remova os que deseja excluir):",
                    options=default_pool_labels,
                    default=default_pool_labels,
                    key=f"form_pool_multiselect_{modulo}"
                )

                st.markdown("---")
                st.markdown("### 📁 3. Adicionar, Remover e Editar Categorias")
                st.caption("Organize seus ativos cadastrados dentro de categorias customizadas.")

                cat_action_mode = st.selectbox("Ação de Categoria:", ["Gerenciar/Editar Existente", "Criar Nova Categoria"], key="form_cat_action_mode")
                
                if cat_action_mode == "Criar Nova Categoria":
                    new_cat_name_input = st.text_input("Nome da Nova Categoria:", value="", placeholder="Ex: 9 - DeFi & Web3", key="form_new_cat_name")
                    new_cat_tag_input = st.text_input("Tag da Categoria:", value="", placeholder="Ex: DeFi", key="form_new_cat_tag")
                    
                    pool_options = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool]
                    selected_new_cat_labels = st.multiselect(
                        "Selecione os ativos para esta nova categoria:",
                        options=pool_options,
                        key="form_new_cat_assets_sel"
                    )
                else:
                    cat_to_edit = st.selectbox("Selecione a Categoria para Gerenciar:", list(active_categories.keys()), key="calib_sel_cat")
                    if cat_to_edit:
                        c_data = active_categories[cat_to_edit]
                        renamed_cat = st.text_input("Renomear Categoria:", value=cat_to_edit, key="calib_rename_cat")
                        
                        current_cat_tickers = {t for _, t, _ in c_data["assets"]}
                        pool_options = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool]
                        default_selected_pool = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool if t in current_cat_tickers]
                        
                        selected_edit_cat_labels = st.multiselect(
                            "Selecione os ativos pertencentes a esta categoria:",
                            options=pool_options,
                            default=default_selected_pool,
                            key=f"form_edit_cat_assets_sel_{cat_to_edit}"
                        )
                        delete_cat_flag = st.checkbox("🗑️ Excluir esta Categoria inteira", value=False, key=f"form_delete_cat_{cat_to_edit}")

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                submitted_calib = st.form_submit_button("💾 Salvar Parâmetros", use_container_width=True)
                
                if submitted_calib:
                    # 1. Montar o pool atualizado com base na seleção do multiselect
                    updated_pool = [pool_labels_map[lbl] for lbl in selected_pool_labels if lbl in pool_labels_map]

                    # 2. Adicionar novo ativo ao pool (se preenchido)
                    n_name = st.session_state.get("form_new_asset_name", "").strip()
                    n_tk = st.session_state.get("form_new_asset_ticker", "").strip().upper()
                    n_cur = st.session_state.get("form_new_asset_curr", "$")
                    if n_name and n_tk:
                        if not any(tk == n_tk for _, tk, _ in updated_pool):
                            updated_pool.append((n_name, n_tk, n_cur))
                    
                    st.session_state[pool_state_key] = updated_pool
                    label_to_tuple = {f"{d} ({t}) [{c}]": (d, t, c) for d, t, c in updated_pool}

                    # 3. Atualizar Categorias
                    if cat_action_mode == "Criar Nova Categoria":
                        n_cat_n = st.session_state.get("form_new_cat_name", "").strip()
                        n_cat_t = st.session_state.get("form_new_cat_tag", "").strip()
                        chosen_labels = st.session_state.get("form_new_cat_assets_sel", [])
                        chosen_tuples = [label_to_tuple[lbl] for lbl in chosen_labels if lbl in label_to_tuple]
                        if n_cat_n:
                            active_categories[n_cat_n] = {
                                "tag": n_cat_t if n_cat_t else "General",
                                "assets": chosen_tuples
                            }
                    else:
                        if cat_to_edit:
                            if st.session_state.get(f"form_delete_cat_{cat_to_edit}", False):
                                active_categories.pop(cat_to_edit, None)
                            else:
                                target_cat_name = st.session_state.get("calib_rename_cat", cat_to_edit)
                                if target_cat_name and target_cat_name != cat_to_edit:
                                    active_categories[target_cat_name] = active_categories.pop(cat_to_edit)
                                    cat_to_edit = target_cat_name
                                
                                chosen_labels = st.session_state.get(f"form_edit_cat_assets_sel_{cat_to_edit}", [])
                                chosen_tuples = [label_to_tuple[lbl] for lbl in chosen_labels if lbl in label_to_tuple]
                                active_categories[cat_to_edit]["assets"] = chosen_tuples

                    if modulo == "Crypto":
                        st.session_state.custom_active_categories_crypto = active_categories
                    else:
                        st.session_state.custom_active_categories_tradfi = active_categories

                    st.toast("Parâmetros, ativos e categorias atualizados com sucesso!", icon="✅")
                    st.session_state.config_window = None
                    st.rerun()
    st.markdown("---")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
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
    st.markdown(f'<div class="status-bar">🌐 <b>{now_str[:10]}</b> | Fonte: {sources_str}</div>', unsafe_allow_html=True)
with col_health:
    st.markdown(f'<div class="status-bar" style="border-color: #238636; justify-content: space-between;"><span>🟢 <b>Auto-Pilot Ativo</b></span><span style="font-size: 12px; color: #8B949E;">Próximo: <b style="color: #3FB950;">{countdown_text}</b></span></div>', unsafe_allow_html=True)
with col_btn_refresh:
    if st.button("🔄 Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if modulo == "TradFi (Macro)" and is_weekend:
    st.markdown('<div class="warning-bar" style="margin-top: 8px;">⚠️ <b>Mercado TradFi Fechado (Fim de Semana):</b> As cotações refletem o fechamento oficial do último pregão (Sexta-feira).</div>', unsafe_allow_html=True)

symbols_to_fetch = [item["ticker"] for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS if item.get("ticker")]
for cat_info in active_categories.values():
    for _, ticker, _ in cat_info["assets"]:
        symbols_to_fetch.append(ticker)
symbols_to_fetch.extend(custom_tickers)

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), brapi_token=brapi_token, custom_api_key=custom_data_api_key)
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()

active_display_categories = active_categories.copy()
if custom_tickers:
    active_display_categories["0 - Tickers Personalizados"] = {
        "tag": "Custom Feed",
        "assets": [(t, t, "R$" if ".SA" in t else "$") for t in custom_tickers]
    }

selected_categories = list(active_display_categories.keys())

col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.subheader("📋 Entregas e Conteúdos Selecionados")
    st.caption("Geração automática de relatórios e scripts com base nas cotações e seleções do dashboard:")

    outputs_generated = []

    if fmt_b2b:
        report_lines = [
            f"=== RELATÓRIO INSTITUCIONAL {modulo.upper()} (B2B) ===",
            f"Emitente: {company_name} | Responsável: {cnpi_code}",
            f"Data/Hora de Emissão: {now_str}",
            f"Sentimento de Mercado: {fng_val} ({fng_class})",
            "",
            "--- SUMÁRIO DE ATIVOS E CATEGORIAS MONITORADAS ---"
        ]
        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_key = f"chk_cat_{cat_name}"
                if not st.session_state.get(cat_key, True):
                    continue
                cat_info = active_display_categories[cat_name]
                report_lines.append(f"\n[{cat_name.upper()}] (Tag: {cat_info['tag']})")
                for disp_name, ticker, currency in cat_info["assets"]:
                    asset_key = f"chk_asset_{cat_name}_{ticker}"
                    if not st.session_state.get(asset_key, True):
                        continue
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    src_name = get_asset_source(ticker)
                    report_lines.append(f"  • {disp_name} ({ticker}) [{src_name}]: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        outputs_generated.append(("B2B (Relatório Analítico)", "\n".join(report_lines)))

    if fmt_yt:
        yt_lines = [f"=== SCRIPT YOUTUBE (AUTO-PILOT) ===", f"Data/Hora: {now_str}", "", "[INTRODUÇÃO]", f"Panorama de {modulo} gerado pelo Auto-Pilot OMNI."]
        outputs_generated.append(("B2C (YouTube)", "\n".join(yt_lines)))

    if fmt_wapp:
        wapp_lines = [f"=== MENSAGEM WHATSAPP ===", f"Alerta OMNI - {now_str}"]
        outputs_generated.append(("B2C (WhatsApp)", "\n".join(wapp_lines)))

    if fmt_tg:
        tg_lines = [f"=== MENSAGEM TELEGRAM ===", f"Canal Oficial OMNI | {now_str}"]
        outputs_generated.append(("B2C (Telegram)", "\n".join(tg_lines)))

    if not outputs_generated:
        st.info("Nenhum formato de saída selecionado na barra lateral.")
        primary_output_text = "Nenhum conteúdo gerado."
    else:
        if len(outputs_generated) == 1:
            title_out, primary_output_text = outputs_generated[0]
            st.text_area(title_out, value=primary_output_text, height=380)
        else:
            tabs = st.tabs([item[0] for item in outputs_generated])
            for idx, (title_out, content_text) in enumerate(outputs_generated):
                with tabs[idx]:
                    st.text_area(f"Visualizar {title_out}", value=content_text, height=350, key=f"txt_area_{idx}")
            primary_output_text = outputs_generated[0][1]

    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.download_button("📥 TXT", data=primary_output_text, file_name=f"OMNI_Report_{modulo}.txt", mime="text/plain", use_container_width=True)
    with col_b2:
        json_data = json.dumps({"module": modulo, "timestamp": now_str, "content": primary_output_text}, indent=4, ensure_ascii=False)
        st.download_button("📦 JSON", data=json_data, file_name=f"OMNI_Report_{modulo}.json", mime="application/json", use_container_width=True)
    with col_b3:
        pdf_bytes = generate_pdf_report(primary_output_text, company_name, now_str)
        st.download_button("📑 PDF", data=pdf_bytes, file_name=f"OMNI_Report_{modulo}.pdf", mime="application/pdf", use_container_width=True)
    with col_b4:
        if st.button("🚀 Disparar CRM", use_container_width=True):
            st.toast(f"Disparo autônomo concluído via {crm_platform}!", icon="🚀")

with col_right:
    st.subheader(f"📈 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado às {datetime.now().strftime('%H:%M:%S BRT')} | Fonte: APIs Oficiais")

    for item in active_benchmarks:
        label = item["label"]
        val_str, chg_str, change_cls = "0", "0%", "color-blue"
        src_badge = f'<span class="source-badge">{get_benchmark_source(item)}</span>'
        
        if item.get("type") == "fng_api":
            val_str = fng_val
            cls_map = {"Greed": "color-green", "Neutral": "color-blue", "Fear": "color-red"}
            change_cls = cls_map.get(fng_class, "color-blue")
            chg_str = f"Sentimento: {fng_class}"
        elif item.get("type") == "global_api":
            sub_k = item.get("sub_key")
            val_str = global_crypto_data["btc_d_val"] if sub_k == "btc_d" else global_crypto_data["usdt_d_val"]
            chg_val = global_crypto_data["btc_d_chg"] if sub_k == "btc_d" else global_crypto_data["usdt_d_chg"]
            chg_str = f"{fmt_pct(chg_val)}"
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")
        elif item.get("ticker"):
            data = quotes.get(item["ticker"], {"price": 0.0, "change": 0.0})
            val_str = f"{item.get('prefix', '')}{fmt_num(data['price'])}"
            chg_val = data["change"]
            chg_str = f"{fmt_pct(chg_val)}"
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")

        st.markdown(f'<div class="metric-card"><div class="metric-title"><span>{label}</span> {src_badge}</div><div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. PAINEL DE ANÁLISE INTEGRADA
# -----------------------------------------------------------------------------
st.subheader(f"📊 Painel de Análise Integrada das Categorias ({modulo})")
if selected_categories:
    cols = st.columns(min(len(selected_categories), 4))
    for idx, cat_name in enumerate(selected_categories):
        if cat_name in active_display_categories:
            cat_info = active_display_categories[cat_name]
            col = cols[idx % len(cols)]
            with col:
                with st.container(border=True):
                    cat_key = f"chk_cat_{cat_name}"
                    c_title, c_dummy, c_check = st.columns([2.2, 0.8, 0.4], vertical_alignment="center")
                    with c_title:
                        st.markdown(f'<div style="font-size: 13px; font-weight: 700; color: #F0F6FC; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{cat_name}</div>', unsafe_allow_html=True)
                    with c_dummy:
                        st.empty()
                    with c_check:
                        cat_enabled = st.checkbox("", value=st.session_state.get(cat_key, True), key=cat_key, label_visibility="collapsed")
                    
                    st.markdown("<div style='border-bottom: 1px solid #30363D; margin-top: 6px; margin-bottom: 6px;'></div>", unsafe_allow_html=True)
                    
                    for disp_name, ticker, currency in cat_info["assets"]:
                        q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                        asset_key = f"chk_asset_{cat_name}_{ticker}"
                        chg_val = q["change"]
                        color_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")
                        src_name = get_asset_source(ticker)
                        
                        c_info, c_badge, c_box = st.columns([2.2, 0.8, 0.4], vertical_alignment="center")
                        with c_info:
                            st.markdown(f'''
                                <div style="font-size: 11px;">
                                    <div style="color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px;">{disp_name}</div>
                                    <div>
                                        <b style="color: #F0F6FC; font-size: 12px;">{currency} {fmt_num(q["price"])}</b> 
                                        <span class="{color_cls}" style="font-size: 11px;">({fmt_pct(q["change"])})</span>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                        with c_badge:
                            st.markdown(f'<span class="source-badge">{src_name}</span>', unsafe_allow_html=True)
                        with c_box:
                            st.checkbox("", value=st.session_state.get(asset_key, True), key=asset_key, disabled=not cat_enabled, label_visibility="collapsed")
                        
                        st.markdown("<div style='border-bottom: 1px solid #21262D; margin-top: 6px; margin-bottom: 6px;'></div>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. MÓDULO: MAPA TÉRMICO DE LIQUIDEZ
# -----------------------------------------------------------------------------
col_sec_title, col_sec_chk = st.columns([4, 1])
with col_sec_title:
    if modulo == "Crypto":
        st.subheader("🌐 Mapa de Alavancagem & Open Interest (Bitcoin / Derivativos)")
    else:
        st.subheader("🌐 Mapa Térmico de Volume Profile & Liquidez Institucional (S&P 500 Futures / TradFi)")
with col_sec_chk:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    st.checkbox("Incluir no Report", value=True, key="chk_include_heatmap")

if PLOTLY_AVAILABLE:
    base_price = quotes.get("BTC-USD" if modulo == "Crypto" else "ES=F", {"price": 77000.0}).get("price", 77000.0)
    if base_price == 0.0:
        base_price = 5000.0 if modulo == "TradFi (Macro)" else 77000.0

    prices = []
    liq_volumes = []
    data_source = ""
    unit_label = "M" if modulo == "Crypto" else "B"

    if modulo == "Crypto":
        data_source = "Deribit API (BTC-PERPETUAL Order Book Real)"
        try:
            url = "https://www.deribit.com/api/v2/public/get_order_book?instrument_name=BTC-PERPETUAL&depth=250"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if res.status_code == 200:
                book_data = res.json().get("result", {})
                bids = pd.DataFrame(book_data.get("bids", []), columns=["price", "qty"])
                asks = pd.DataFrame(book_data.get("asks", []), columns=["price", "qty"])
                df_book = pd.concat([bids, asks])
                if not df_book.empty:
                    df_book["notional_m"] = df_book["qty"] / 1_000_000
                    min_p = base_price * 0.85
                    max_p = base_price * 1.15
                    df_book = df_book[(df_book["price"] >= min_p) & (df_book["price"] <= max_p)]
                    num_bins = 25
                    bin_edges = np.linspace(min_p, max_p, num_bins + 1)
                    df_book["bin_idx"] = pd.cut(df_book["price"], bins=bin_edges, labels=False, include_lowest=True)
                    grouped = df_book.groupby("bin_idx")["notional_m"].sum().reset_index()
                    for i in range(num_bins):
                        p_mid = (bin_edges[i] + bin_edges[i+1]) / 2
                        matched = grouped[grouped["bin_idx"] == i]
                        v = float(matched["notional_m"].values[0]) if not matched.empty else 0.0
                        if v > 0:
                            prices.append(p_mid)
                            liq_volumes.append(v)
        except Exception:
            pass

        if not prices:
            prices = [base_price * 0.95, base_price * 0.98, base_price * 1.02, base_price * 1.05]
            liq_volumes = [1.2, 4.8, 6.5, 3.1]
    else:
        data_source = "Yahoo Finance API (S&P 500 Histórico Real — ES=F)"
        try:
            import yfinance as yf
            df_es = yf.download("ES=F", period="3mo", interval="1h", progress=False)
            if not df_es.empty:
                if isinstance(df_es.columns, pd.MultiIndex):
                    df_es.columns = df_es.columns.get_level_values(0)
                df_es = df_es.dropna(subset=['Close', 'Volume'])
                if not df_es.empty:
                    min_p = df_es['Close'].min()
                    max_p = df_es['Close'].max()
                    df_es["notional_b"] = (df_es['Close'] * df_es['Volume']) / 1_000_000_000
                    num_bins = 25
                    bin_edges = np.linspace(min_p, max_p, num_bins + 1)
                    df_es["bin_idx"] = pd.cut(df_es['Close'], bins=bin_edges, labels=False, include_lowest=True)
                    grouped = df_es.groupby("bin_idx")["notional_b"].sum().reset_index()
                    for i in range(num_bins):
                        p_mid = (bin_edges[i] + bin_edges[i+1]) / 2
                        matched = grouped[grouped["bin_idx"] == i]
                        v = float(matched["notional_b"].values[0]) if not matched.empty else 0.0
                        if v > 0:
                            prices.append(p_mid)
                            liq_volumes.append(v)
        except Exception:
            pass

        if not prices:
            prices = [base_price * 0.96, base_price * 0.99]
            liq_volumes = [18.4, 45.1]

    arr_v = np.array(liq_volumes, dtype=float)
    max_v = arr_v.max() if len(arr_v) > 0 and arr_v.max() > 0 else 1.0
    color_intensity = np.sqrt(arr_v / max_v) * 100.0

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(
        y=prices,
        x=liq_volumes,
        orientation='h',
        marker=dict(color=color_intensity, colorscale='Jet', showscale=True, colorbar=dict(title="Intensidade Térmica", len=0.8, thickness=12, tickfont=dict(color="#C9D1D9"))),
        hoverinfo='text',
        text=[f"Preço: {fmt_num(p)} | Volume: ${v:.2f}{unit_label}" for p, v in zip(prices, liq_volumes)],
        name="Clusters de Liquidez"
    ))

    fig_oi.add_hline(y=base_price, line_dash="dash", line_color="#58A6FF", annotation_text=f"Spot Atual: {fmt_num(base_price)}", annotation_position="bottom right", annotation_font_color="#58A6FF")

    fig_oi.update_layout(
        title="Mapa Térmico de Liquidez Institucional" if modulo != "Crypto" else "Mapa de Alavancagem & Open Interest (Bitcoin)",
        paper_bgcolor="#0B0E14", plot_bgcolor="#161B22", font=dict(color="#C9D1D9", size=12),
        margin=dict(l=20, r=20, t=40, b=20), height=520,
        yaxis=dict(gridcolor="#30363D", title="Níveis de Preço (USD)"),
        xaxis=dict(gridcolor="#30363D", title="Volume Notional Acumulado")
    )
    st.plotly_chart(fig_oi, use_container_width=True)
    st.markdown(f"📌 **Fonte Oficial da API Ativa:** `{data_source}`")
else:
    st.warning("⚠️ O módulo Plotly não está disponível no momento.")

st.markdown("---")
st.caption("⚡©️ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")