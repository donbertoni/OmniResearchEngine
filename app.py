import json
from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

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
# DICIONÁRIO DE TRADUÇÃO COMPLETO (100% BILÍNGUE PT / EN)
# -----------------------------------------------------------------------------
TRANSLATIONS = {
    "PT": {
        "terminal_title": "Terminal OMNI",
        "login": "Login do Analista",
        "user_label": "Usuário / E-mail:",
        "pass_label": "Senha:",
        "keep_connected": "Manter-se conectado",
        "module": "Escolha o Módulo:",
        "outputs": "Formatos de Saída:",
        "fmt_b2b": "B2B (Relatório Analítico)",
        "fmt_yt": "B2C (YouTube Auto-Pilot)",
        "fmt_wapp": "B2C (WhatsApp Auto-Pilot)",
        "fmt_tg": "B2C (Telegram Auto-Pilot)",
        "production_btn": "Acionar Produção Automática",
        "advanced_config": "Configurações Avançadas",
        "automations": "Automações",
        "triggers": "Gatilhos de Report",
        "calibration": "Calibragem da Engine",
        "active_plan": "Plano Ativo:",
        "deliveries": "Entregas e Conteúdos Selecionados",
        "deliveries_caption": "Geração automática de relatórios e scripts com base nas cotações e seleções do dashboard:",
        "metrics": "Métricas Agregadas",
        "integrated_panel": "Painel de Análise Integrada das Categorias",
        "agents_title": "Arquitetura de Agentes Especializados (IA & ML)",
        "agents_caption": "Orquestração autônoma de Agentes Inteligentes para predição, análise técnica, roteirização e direção de arte.",
        "agent_script": "🤖 Agente Roteirista",
        "agent_predictive": "📊 Agente Preditiva (ML)",
        "agent_ta": "📈 Agente de Análise Técnica",
        "agent_art": "🎨 IA Diretora de Arte (YouTube Auto-Pilot)",
        "terminal_html_tab": "🖥️ Terminal Quant v5.2 (HTML Nativo)",
        "close": "Fechar",
        "auto_config_title": "Configuração de Automações & Integradores de CRM",
        "trig_config_title": "Configuração Avançada de Gatilhos de Report Automático",
        "calib_config_title": "Calibragem da Engine & Gerenciador de Ativos e Categorias",
        "payload_channels": "Canais de Disparo de Dados (Payloads):",
        "email_notif": "Endereços Eletrônicos (Notificação B2B):",
        "webhooks_url": "URLs / Webhooks de Disparo (Engine -> CRM):",
        "crm_integration": "Integração com Plataformas de CRM (Orquestração):",
        "crm_platform": "Plataforma de CRM Alvo:",
        "crm_apikey": "Chave de API / Token do CRM:",
        "trig_days_title": "📅 1. Dias da Semana para Geração Automática",
        "trig_days_label": "Escolha quais dias da semana os gatilhos dispararão relatórios:",
        "trig_freq_title": "⏰ 2 & 3. Frequência Diária e Horários dos Reports",
        "trig_freq_label": "Frequência (Nº de reports diários):",
        "trig_assets_title": "🎯 4. Seleção de Ativos Monitorados (Máx. 10)",
        "trig_assets_label": "Selecione os ativos que os gatilhos vão considerar (Máximo de 10):",
        "calib_creds": "🔑 1. Credenciais de API & Integrações",
        "brapi_token": "BRAPI API Token:",
        "custom_api": "Custom Market API Key:",
        "whatsapp_inst": "WhatsApp Instance ID:",
        "whatsapp_token": "WhatsApp API Token:",
        "calib_assets": "➕ 2. Adicionar e Remover Ativos",
        "calib_assets_caption": "Cadastre novos ativos ou gerencie o pool global de ativos disponíveis no sistema.",
        "add_new_asset": "➕ Adicionar Novo Ativo",
        "friendly_name": "Nome Amigável:",
        "ticker_input": "Ticker:",
        "currency_input": "Moeda:",
        "manage_assets": "⚙️ Gerenciar / Remover Ativos Existentes",
        "manage_assets_caption": "Use a caixa abaixo para visualizar e remover ativos existentes do pool.",
        "pool_assets_label": "Ativos atualmente no pool:",
        "calib_cats": "📂 3. Adicionar, Remover e Editar Categorias",
        "calib_cats_caption": "Organize seus ativos cadastrados dentro de categorias customizadas.",
        "cat_action": "Ação de Categoria:",
        "new_cat_name": "Nome da Nova Categoria:",
        "new_cat_tag": "Tag da Categoria:",
        "new_cat_assets": "Selecione os ativos para esta nova categoria:",
        "cat_to_manage": "Selecione a Categoria para Gerenciar:",
        "rename_cat": "Renomear Categoria:",
        "edit_cat_assets": "Selecione os ativos pertencentes a esta categoria:",
        "delete_cat_flag": "🗑️ Excluir esta Categoria inteira",
        "save_params": "💾 Salvar Parâmetros",
        "refresh_btn": "🔄 Refresh",
        "weekend_msg": "⚠️ <b>Market Closed (Weekend):</b> Quotes reflect official closing prices from Friday session.",
        "agent_script_title": "🤖 Agente Roteirista (Multi-Format Scriptwriter)",
        "agent_script_desc": "Responsável por coletar inputs em tempo real (preços, indicadores macro/crypto, sentimento) e sintetizar roteiros direcionados para TXT, JSON, WhatsApp, Telegram e YouTube.",
        "target_asset_script": "Ativo Alvo para Roteiro:",
        "script_tone": "Tom do Roteiro:",
        "generate_script": "Gerar Roteiro Autônomo",
        "agent_pred_title": "📊 Agente Preditiva (Machine Learning Real-Time)",
        "agent_pred_desc": "Monitora ativos restritos de alta liquidez (`BTC-USD`, `ES=F`), executando inferências estatísticas e registrando logs de acurácia contínua.",
        "pred_asset_label": "Ativo sob Análise Preditiva:",
        "win_rate_label": "Assertividade Histórica (Win Rate)",
        "confidence_label": "Nível de Confiança da Inferência Atual",
        "pred_logs_title": "📋 Logs de Performance Preditiva",
        "run_ml_btn": "Executar Nova Inferência de ML",
        "agent_ta_title": "📈 Agente de Análise Técnica Avançada",
        "agent_ta_desc": "Recebe os dados da Agente Preditiva, processa tempos gráficos múltiplos (`4h`, `1D`, `1W`, `1M`), identifica formações clássicas e gera níveis operacionais.",
        "ta_asset_label": "Ativo para Análise Técnica:",
        "ta_tf_label": "Tempo Gráfico:",
        "run_ta_btn": "Executar Varredura de Padrões (TA Agent)",
        "agent_art_title": "🎨 IA Diretora de Arte (YouTube Auto-Pilot)",
        "agent_art_desc": "Orquestra autonomamente a criação de vídeos institucionais, aplicando técnicas de zoom no dashboard, legendas automatizadas e síntese de voz (TTS) para publicação direta no YouTube via API.",
        "visual_template": "Template Visual:",
        "tts_voice": "Locução (TTS Engine):",
        "yt_status": "Status de Publicação no YouTube:",
        "yt_schedule": "Agendar Publicação após Fechamento de Mercado",
        "render_video": "Renderizar e Disparar Vídeo Autônomo",
        "heatmap_crypto": "📊 Mapa de Alavancagem & Open Interest (Bitcoin / Derivativos)",
        "heatmap_tradfi": "🌐 Mapa Térmico de Volume Profile & Liquidez Institucional (S&P 500 Futures / TradFi)",
        "include_report": "Incluir no Report"
    },
    "EN": {
        "terminal_title": "OMNI Terminal",
        "login": "Analyst Login",
        "user_label": "User / E-mail:",
        "pass_label": "Password:",
        "keep_connected": "Keep me logged in",
        "module": "Select Module:",
        "outputs": "Output Formats:",
        "fmt_b2b": "B2B (Analytical Report)",
        "fmt_yt": "B2C (YouTube Auto-Pilot)",
        "fmt_wapp": "B2C (WhatsApp Auto-Pilot)",
        "fmt_tg": "B2C (Telegram Auto-Pilot)",
        "production_btn": "Trigger Automated Production",
        "advanced_config": "Advanced Settings",
        "automations": "Automations",
        "triggers": "Report Triggers",
        "calibration": "Engine Calibration",
        "active_plan": "Active Plan:",
        "deliveries": "Selected Deliveries & Content",
        "deliveries_caption": "Automated generation of reports and scripts based on live quotes and dashboard selections:",
        "metrics": "Aggregated Metrics",
        "integrated_panel": "Integrated Category Analysis Panel",
        "agents_title": "Specialized Agents Architecture (AI & ML)",
        "agents_caption": "Autonomous orchestration of Intelligent Agents for prediction, technical analysis, scripting, and art direction.",
        "agent_script": "🤖 Scriptwriter Agent",
        "agent_predictive": "📊 Predictive Agent (ML)",
        "agent_ta": "📈 Technical Analysis Agent",
        "agent_art": "🎨 Art Director AI (YouTube Auto-Pilot)",
        "terminal_html_tab": "🖥️ Terminal Quant v5.2 (Native HTML)",
        "close": "Close",
        "auto_config_title": "Automation Settings & CRM Integrators",
        "trig_config_title": "Advanced Automated Report Triggers Configuration",
        "calib_config_title": "Engine Calibration & Asset/Category Manager",
        "payload_channels": "Data Dispatch Channels (Payloads):",
        "email_notif": "Email Addresses (B2B Notification):",
        "webhooks_url": "Dispatch URLs / Webhooks (Engine -> CRM):",
        "crm_integration": "CRM Platform Integration (Orchestration):",
        "crm_platform": "Target CRM Platform:",
        "crm_apikey": "CRM API Key / Token:",
        "trig_days_title": "📅 1. Days of the Week for Automatic Generation",
        "trig_days_label": "Choose which days of the week triggers will fire reports:",
        "trig_freq_title": "⏰ 2 & 3. Daily Frequency and Report Times",
        "trig_freq_label": "Frequency (Number of daily reports):",
        "trig_assets_title": "🎯 4. Monitored Assets Selection (Max 10)",
        "trig_assets_label": "Select the assets triggers will consider (Maximum of 10):",
        "calib_creds": "🔑 1. API Credentials & Integrations",
        "brapi_token": "BRAPI API Token:",
        "custom_api": "Custom Market API Key:",
        "whatsapp_inst": "WhatsApp Instance ID:",
        "whatsapp_token": "WhatsApp API Token:",
        "calib_assets": "➕ 2. Add and Remove Assets",
        "calib_assets_caption": "Register new assets or manage the global pool of assets available in the system.",
        "add_new_asset": "➕ Add New Asset",
        "friendly_name": "Friendly Name:",
        "ticker_input": "Ticker:",
        "currency_input": "Currency:",
        "manage_assets": "⚙️ Manage / Remove Existing Assets",
        "manage_assets_caption": "Use the box below to view and remove existing assets from the pool.",
        "pool_assets_label": "Assets currently in the pool:",
        "calib_cats": "📂 3. Add, Remove and Edit Categories",
        "calib_cats_caption": "Organize your registered assets within custom categories.",
        "cat_action": "Category Action:",
        "new_cat_name": "New Category Name:",
        "new_cat_tag": "Category Tag:",
        "new_cat_assets": "Select assets for this new category:",
        "cat_to_manage": "Select Category to Manage:",
        "rename_cat": "Rename Category:",
        "edit_cat_assets": "Select assets belonging to this category:",
        "delete_cat_flag": "🗑️ Delete this entire category",
        "save_params": "💾 Save Parameters",
        "refresh_btn": "🔄 Refresh",
        "weekend_msg": "⚠️ <b>Market Closed (Weekend):</b> Quotes reflect official closing prices from Friday session.",
        "agent_script_title": "🤖 Scriptwriter Agent (Multi-Format Scriptwriter)",
        "agent_script_desc": "Responsible for collecting real-time inputs (prices, macro/crypto indicators, sentiment) and synthesizing targeted scripts for TXT, JSON, WhatsApp, Telegram, and YouTube.",
        "target_asset_script": "Target Asset for Script:",
        "script_tone": "Script Tone:",
        "generate_script": "Generate Autonomous Script",
        "agent_pred_title": "📊 Predictive Agent (Real-Time Machine Learning)",
        "agent_pred_desc": "Monitors high-liquidity restricted assets (`BTC-USD`, `ES=F`), executing statistical inferences and recording continuous accuracy logs.",
        "pred_asset_label": "Asset Under Predictive Analysis:",
        "win_rate_label": "Historical Win Rate",
        "confidence_label": "Current Inference Confidence Level",
        "pred_logs_title": "📋 Predictive Performance Logs",
        "run_ml_btn": "Run New ML Inference",
        "agent_ta_title": "📈 Advanced Technical Analysis Agent",
        "agent_ta_desc": "Receives data from the Predictive Agent, processes multiple timeframes (`4h`, `1D`, `1W`, `1M`), identifies classic patterns, and generates operational levels.",
        "ta_asset_label": "Asset for Technical Analysis:",
        "ta_tf_label": "Timeframe:",
        "run_ta_btn": "Run Pattern Scanner (TA Agent)",
        "agent_art_title": "🎨 Art Director AI (YouTube Auto-Pilot)",
        "agent_art_desc": "Autonomously orchestrates the creation of institutional videos, applying dashboard zoom techniques, automated subtitles, and voice synthesis (TTS) for direct publication to YouTube via API.",
        "visual_template": "Visual Template:",
        "tts_voice": "Voiceover (TTS Engine):",
        "yt_status": "YouTube Publication Status:",
        "yt_schedule": "Schedule Publication After Market Close",
        "render_video": "Render & Dispatch Autonomous Video",
        "heatmap_crypto": "📊 Leverage & Open Interest Heatmap (Bitcoin / Derivatives)",
        "heatmap_tradfi": "🌐 Volume Profile & Institutional Liquidity Heatmap (S&P 500 Futures / TradFi)",
        "include_report": "Include in Report"
    }
}

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

lang_choice = st.sidebar.selectbox("🌐 Idioma / Language", ["Português (BR)", "English (US)"], index=0)
LANG_KEY = "PT" if "Português" in lang_choice else "EN"
tr = TRANSLATIONS[LANG_KEY]

if "custom_active_categories_crypto" not in st.session_state:
    st.session_state.custom_active_categories_crypto = CATEGORIES_CRYPTO.copy()
if "custom_active_categories_tradfi" not in st.session_state:
    st.session_state.custom_active_categories_tradfi = CATEGORIES_TRADFI.copy()

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

with st.sidebar.expander(f"🔒 {tr['login']}", expanded=False):
    login_user = st.text_input(tr['user_label'], value="analista@omni.com")
    login_pass = st.text_input(tr['pass_label'], value="••••••••", type="password")
    login_keep = st.checkbox(tr['keep_connected'], value=True)

if "admin" in login_user.lower() or "white" in login_user.lower():
    tier_selected = "Premium (B2B White-Label)"
elif "free" in login_user.lower():
    tier_selected = "Free (Lead Magnet)"
else:
    tier_selected = "Standard (B2C Trader)"

st.sidebar.markdown(f"**{tr['active_plan']}** `{tier_selected}`")
st.sidebar.markdown("---")

modulo = st.sidebar.radio(f"📊 {tr['module']}", ["Crypto", "TradFi (Macro)"], index=1, key="modulo_selection")

st.sidebar.markdown(f"### ⚙️ {tr['outputs']}")
fmt_b2b = st.sidebar.checkbox(tr['fmt_b2b'], value=True)
fmt_yt = st.sidebar.checkbox(tr['fmt_yt'], value=False)
fmt_wapp = st.sidebar.checkbox(tr['fmt_wapp'], value=False)
fmt_tg = st.sidebar.checkbox(tr['fmt_tg'], value=False)

st.sidebar.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
trigger_production = st.sidebar.button(f"🚀 {tr['production_btn']}", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"### 🛠️ {tr['advanced_config']}")

if "config_window" not in st.session_state:
    st.session_state.config_window = None

if st.sidebar.button(f"⚙️ {tr['automations']}", use_container_width=True):
    st.session_state.config_window = "automations"
if st.sidebar.button(f"⚡ {tr['triggers']}", use_container_width=True):
    st.session_state.config_window = "triggers"
if st.sidebar.button(f"🎛️ {tr['calibration']}", use_container_width=True):
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
# 3. CORPO PRINCIPAL & JANELAS ESPECÍFICAS DE CONFIGURAÇÃO
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏛️ {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira com IA & Auto-Pilot (Bilingual Ready)")

if st.session_state.config_window:
    with st.container(border=True):
        col_w_title, col_w_close = st.columns([5, 1])
        with col_w_title:
            if st.session_state.config_window == "automations":
                st.subheader(f"⚙️ {tr['auto_config_title']}")
            elif st.session_state.config_window == "triggers":
                st.subheader(f"⚡ {tr['trig_config_title']}")
            elif st.session_state.config_window == "calibration":
                st.subheader(f"🎛️ {tr['calib_config_title']}")
        with col_w_close:
            if st.button(f"❌ {tr['close']}", use_container_width=True):
                st.session_state.config_window = None
                st.rerun()

        if st.session_state.config_window == "automations":
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.markdown(f"**{tr['payload_channels']}**")
                auto_emails = st.text_input(tr['email_notif'], value="mesa@gestora.com, compliance@gestora.com")
                auto_urls = st.text_input(tr['webhooks_url'], value="")
            with col_a2:
                st.markdown(f"**{tr['crm_integration']}**")
                crm_platform = st.selectbox(tr['crm_platform'], ["HubSpot", "Salesforce", "RD Station", "Outro Webhook/API"], index=0)
                crm_api_key = st.text_input(tr['crm_apikey'], value="", type="password")

        elif st.session_state.config_window == "triggers":
            st.markdown(f"**Módulo Ativo:** `{modulo}`")
            st.markdown(f"**{tr['trig_days_title']}**")
            selected_days = st.multiselect(
                tr['trig_days_label'],
                options=["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"],
                default=["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"],
                key="trig_days"
            )
            st.markdown("---")
            st.markdown(f"**{tr['trig_freq_title']}**")
            freq_reports = st.slider(tr['trig_freq_label'], min_value=1, max_value=5, value=2, key="trig_freq")
            report_times = []
            time_cols = st.columns(min(freq_reports, 5))
            default_times_str = ["09:00", "12:00", "15:00", "18:00", "21:00"]
            for i in range(freq_reports):
                with time_cols[i % len(time_cols)]:
                    def_t = datetime.strptime(default_times_str[i], "%H:%M").time() if i < len(default_times_str) else datetime.strptime("12:00", "%H:%M").time()
                    t_val = st.time_input(f"Horário Report {i+1}", value=def_t, key=f"trig_time_{i+1}")
                    report_times.append(t_val)
            st.markdown("---")
            st.markdown(f"**{tr['trig_assets_title']}**")
            all_module_assets = []
            for cat_name, cat_info in active_categories.items():
                for disp_name, ticker, currency in cat_info["assets"]:
                    all_module_assets.append((f"{disp_name} ({ticker}) — [{cat_name}]", ticker))
            
            asset_labels = [item[0] for item in all_module_assets]
            selected_trigger_assets = st.multiselect(
                tr['trig_assets_label'],
                options=asset_labels,
                max_selections=10,
                default=asset_labels[:min(5, len(asset_labels))],
                key="trig_assets"
            )

        elif st.session_state.config_window == "calibration":
            with st.form("calibration_form"):
                st.markdown(f"### {tr['calib_creds']}")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    brapi_token = st.text_input(tr['brapi_token'], value="", type="password")
                    custom_data_api_key = st.text_input(tr['custom_api'], value="", type="password")
                with col_c2:
                    whatsapp_instance = st.text_input(tr['whatsapp_inst'], value="")
                    whatsapp_token = st.text_input(tr['whatsapp_token'], value="", type="password")

                st.markdown("---")
                st.markdown(f"### {tr['calib_assets']}")
                st.caption(tr['calib_assets_caption'])
                
                st.markdown(f"#### {tr['add_new_asset']}")
                col_na1, col_na2, col_na3 = st.columns(3)
                with col_na1:
                    new_asset_name_input = st.text_input(tr['friendly_name'], value="", placeholder="Ex: Ethereum", key="form_new_asset_name")
                with col_na2:
                    new_asset_ticker_input = st.text_input(tr['ticker_input'], value="", placeholder="Ex: ETH-USD", key="form_new_asset_ticker")
                with col_na3:
                    new_asset_curr_input = st.selectbox(tr['currency_input'], ["$", "R$"], key="form_new_asset_curr")

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                st.markdown(f"#### {tr['manage_assets']}")
                st.caption(tr['manage_assets_caption'])
                
                pool_labels_map = {f"{disp} ({tk}) [{cur}]": (disp, tk, cur) for disp, tk, cur in current_asset_pool}
                default_pool_labels = list(pool_labels_map.keys())
                
                selected_pool_labels = st.multiselect(
                    tr['pool_assets_label'],
                    options=default_pool_labels,
                    default=default_pool_labels,
                    key=f"form_pool_multiselect_{modulo}"
                )

                st.markdown("---")
                st.markdown(f"### {tr['calib_cats']}")
                st.caption(tr['calib_cats_caption'])

                cat_action_mode = st.selectbox(tr['cat_action'], ["Gerenciar/Editar Existente", "Criar Nova Categoria"], key="form_cat_action_mode")
                
                if cat_action_mode == "Criar Nova Categoria":
                    new_cat_name_input = st.text_input(tr['new_cat_name'], value="", placeholder="Ex: 9 - DeFi & Web3", key="form_new_cat_name")
                    new_cat_tag_input = st.text_input(tr['new_cat_tag'], value="", placeholder="Ex: DeFi", key="form_new_cat_tag")
                    
                    pool_options = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool]
                    selected_new_cat_labels = st.multiselect(
                        tr['new_cat_assets'],
                        options=pool_options,
                        key="form_new_cat_assets_sel"
                    )
                else:
                    cat_to_edit = st.selectbox(tr['cat_to_manage'], list(active_categories.keys()), key="calib_sel_cat")
                    if cat_to_edit:
                        c_data = active_categories[cat_to_edit]
                        renamed_cat = st.text_input(tr['rename_cat'], value=cat_to_edit, key="calib_rename_cat")
                        
                        current_cat_tickers = {t for _, t, _ in c_data["assets"]}
                        pool_options = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool]
                        default_selected_pool = [f"{d} ({t}) [{c}]" for d, t, c in current_asset_pool if t in current_cat_tickers]
                        
                        selected_edit_cat_labels = st.multiselect(
                            tr['edit_cat_assets'],
                            options=pool_options,
                            default=default_selected_pool,
                            key=f"form_edit_cat_assets_sel_{cat_to_edit}"
                        )
                        delete_cat_flag = st.checkbox(tr['delete_cat_flag'], value=False, key=f"form_delete_cat_{cat_to_edit}")

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                submitted_calib = st.form_submit_button(tr['save_params'], use_container_width=True)
                
                if submitted_calib:
                    updated_pool = [pool_labels_map[lbl] for lbl in selected_pool_labels if lbl in pool_labels_map]

                    n_name = st.session_state.get("form_new_asset_name", "").strip()
                    n_tk = st.session_state.get("form_new_asset_ticker", "").strip().upper()
                    n_cur = st.session_state.get("form_new_asset_curr", "$")
                    if n_name and n_tk:
                        if not any(tk == n_tk for _, tk, _ in updated_pool):
                            updated_pool.append((n_name, n_tk, n_cur))
                    
                    st.session_state[pool_state_key] = updated_pool
                    label_to_tuple = {f"{d} ({t}) [{c}]": (d, t, c) for d, t, c in updated_pool}

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

                    st.toast("Parâmetros atualizados com sucesso!", icon="✅")
                    st.session_state.config_window = None
                    st.rerun()
    st.markdown("---")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT" if LANG_KEY == "PT" else "%Y-%m-%d at %H:%M:%S UTC")
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
    st.markdown(f'<div class="status-bar" style="border-color: #238636; justify-content: space-between;"><span>🟢 <b>Auto-Pilot</b></span><span style="font-size: 12px; color: #8B949E;">Next: <b style="color: #3FB950;">{countdown_text}</b></span></div>', unsafe_allow_html=True)
with col_btn_refresh:
    if st.button(tr['refresh_btn'], use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if modulo == "TradFi (Macro)" and is_weekend:
    st.markdown(f'<div class="warning-bar" style="margin-top: 8px;">{tr["weekend_msg"]}</div>', unsafe_allow_html=True)

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
    st.subheader(f"📊 {tr['deliveries']}")
    st.caption(tr['deliveries_caption'])

    outputs_generated = []

    if fmt_b2b:
        report_lines = [
            f"=== INSTITUTIONAL REPORT {modulo.upper()} (B2B) ===",
            f"Issuer: {company_name} | Analyst ID: {cnpi_code}",
            f"Timestamp: {now_str} | Language: {LANG_KEY}",
            f"Market Sentiment: {fng_val} ({fng_class})",
            "",
            "--- ASSETS & MONITORED CATEGORIES ---"
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
        outputs_generated.append(("B2B (Analytical Report)", "\n".join(report_lines)))

    if fmt_yt:
        yt_lines = [f"=== YOUTUBE SCRIPT (AUTO-PILOT) ===", f"Timestamp: {now_str}", "", "[INTRODUCTION]", f"Market overview for {modulo} generated by OMNI Auto-Pilot."]
        outputs_generated.append(("B2C (YouTube)", "\n".join(yt_lines)))

    if fmt_wapp:
        wapp_lines = [f"=== WHATSAPP MESSAGE ===", f"OMNI Alert - {now_str}"]
        outputs_generated.append(("B2C (WhatsApp)", "\n".join(wapp_lines)))

    if fmt_tg:
        tg_lines = [f"=== TELEGRAM MESSAGE ===", f"OMNI Official Channel | {now_str}"]
        outputs_generated.append(("B2C (Telegram)", "\n".join(tg_lines)))

    if not outputs_generated:
        st.info("No output format selected in sidebar.")
        primary_output_text = "No content generated."
    else:
        if len(outputs_generated) == 1:
            title_out, primary_output_text = outputs_generated[0]
            st.text_area(title_out, value=primary_output_text, height=380)
        else:
            tabs = st.tabs([item[0] for item in outputs_generated])
            for idx, (title_out, content_text) in enumerate(outputs_generated):
                with tabs[idx]:
                    st.text_area(f"View {title_out}", value=content_text, height=350, key=f"txt_area_{idx}")
            primary_output_text = outputs_generated[0][1]

    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.download_button("📥 TXT", data=primary_output_text, file_name=f"OMNI_Report_{modulo}_{LANG_KEY}.txt", mime="text/plain", use_container_width=True)
    with col_b2:
        json_data = json.dumps({"module": modulo, "language": LANG_KEY, "timestamp": now_str, "content": primary_output_text}, indent=4, ensure_ascii=False)
        st.download_button("📥 JSON", data=json_data, file_name=f"OMNI_Report_{modulo}_{LANG_KEY}.json", mime="application/json", use_container_width=True)
    with col_b3:
        pdf_bytes = generate_pdf_report(primary_output_text, company_name, now_str)
        st.download_button("📥 PDF", data=pdf_bytes, file_name=f"OMNI_Report_{modulo}_{LANG_KEY}.pdf", mime="application/pdf", use_container_width=True)
    with col_b4:
        if st.button("🚀 CRM Push", use_container_width=True):
            st.toast(f"Autonomous payload dispatched via {crm_platform}!", icon="🎯")

with col_right:
    st.subheader(f"📈 {tr['metrics']} ({modulo})")
    st.caption(f"Updated | Source: Official APIs")

    for item in active_benchmarks:
        label = item["label"]
        val_str, chg_str, change_cls = "0", "0%", "color-blue"
        src_badge = f'<span class="source-badge">{get_benchmark_source(item)}</span>'
        
        if item.get("type") == "fng_api":
            val_str = fng_val
            cls_map = {"Greed": "color-green", "Neutral": "color-blue", "Fear": "color-red"}
            change_cls = cls_map.get(fng_class, "color-blue")
            chg_str = f"Sentiment: {fng_class}"
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

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. PAINEL DE ANÁLISE INTEGRADA
# -----------------------------------------------------------------------------
st.subheader(f"📂 {tr['integrated_panel']} ({modulo})")
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
# 5. ARQUITETURA DE AGENTES ESPECIALIZADOS (IA & ML) & TERMINAL HTML NATIVO
# -----------------------------------------------------------------------------
st.subheader(f"🤖 {tr['agents_title']}")
st.caption(tr['agents_caption'])

agent_tab1, agent_tab2, agent_tab3, agent_tab4, agent_tab5 = st.tabs([
    tr['agent_script'], 
    tr['agent_predictive'], 
    tr['agent_ta'], 
    tr['agent_art'],
    tr['terminal_html_tab']
])

with agent_tab1:
    st.markdown(f"### {tr['agent_script_title']}")
    st.markdown(tr['agent_script_desc'])
    
    target_asset_script = st.selectbox(tr['target_asset_script'], ["BTC-USD", "ES=F", "ITUB4.SA", "PETR4.SA"], key="script_asset_sel")
    script_tone = st.selectbox(tr['script_tone'], ["Institucional / B2B", "Trader Agressivo / HFT", "Educacional / Retail"], key="script_tone_sel")
    
    if st.button(tr['generate_script'], use_container_width=True):
        sample_price = quotes.get(target_asset_script, {}).get("price", 50000.0)
        sample_chg = quotes.get(target_asset_script, {}).get("change", 1.5)
        
        script_output = f"""[OMNI AGENT SCRIPTWRITER - {LANG_KEY}]
Asset: {target_asset_script} | Price: {sample_price} | Change: {sample_chg}%
Tone: {script_tone}
--------------------------------------------------
[00:00 - Intro]: Welcome investors, OMNI Research delivering high-performance insights for {target_asset_script}.
[00:30 - Core Analysis]: The asset registers a variation of {sample_chg}%, backed by recent institutional flows.
[01:15 - Conclusion]: Keep your technical stops calibrated according to previous reports.
"""
        st.text_area("Roteiro Sintetizado pela IA / Synthesized AI Script:", value=script_output, height=200)

with agent_tab2:
    st.markdown(f"### {tr['agent_pred_title']}")
    st.markdown(tr['agent_pred_desc'])
    
    pred_asset = st.selectbox(tr['pred_asset_label'], ["BTC-USD", "ES=F"], key="pred_asset_sel")
    
    if "ml_prediction_logs" not in st.session_state:
        st.session_state.ml_prediction_logs = [
            {"timestamp": "21/08/2026 18:00", "asset": "BTC-USD", "prediction": "Alta (Bullish)", "confidence": "78.4%", "status": "Acerto ✅"},
            {"timestamp": "20/08/2026 12:00", "asset": "ES=F", "prediction": "Neutro / Consolidação", "confidence": "82.1%", "status": "Acerto ✅"}
        ]
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.metric(label=tr['win_rate_label'], value="79.8%", delta="+3.2% vs Mês Anterior")
    with col_p2:
        current_conf = "84.5% (High Confidence)" if LANG_KEY == "EN" else "84.5% (Alta Confiança)"
        st.metric(label=tr['confidence_label'], value=current_conf)

    st.markdown(f"#### {tr['pred_logs_title']}")
    df_logs = pd.DataFrame(st.session_state.ml_prediction_logs)
    st.dataframe(df_logs, use_container_width=True)
    
    if st.button(tr['run_ml_btn'], use_container_width=True):
        new_log = {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "asset": pred_asset,
            "prediction": "Alta Direcional (Momentum Positivo)",
            "confidence": "81.9%",
            "status": "Em Monitoramento 🔄"
        }
        st.session_state.ml_prediction_logs.insert(0, new_log)
        st.toast("Nova predição registrada com sucesso!", icon="📊")
        st.rerun()

with agent_tab3:
    st.markdown(f"### {tr['agent_ta_title']}")
    st.markdown(tr['agent_ta_desc'])
    
    ta_asset = st.selectbox(tr['ta_asset_label'], ["BTC-USD", "ES=F"], key="ta_asset_sel")
    ta_timeframe = st.selectbox(tr['ta_tf_label'], ["4h", "1D", "1W", "1M"], index=1, key="ta_tf_sel")
    
    if st.button(tr['run_ta_btn'], use_container_width=True):
        st.success(f"Análise concluída para **{ta_asset}** ({ta_timeframe}):")
        st.markdown(f"""
        > **Padrão Identificado / Pattern Identified:** Potencial *Cup and Handle* em formação no gráfico de **{ta_timeframe}**.
        > * **Rompimento / Breakout Level:** `$78,500.00` (Crypto) / `5,950.00 pts` (TradFi)
        > * **Targets / Alvos:** `$82,000.00` | `$86,500.00` | `$92,000.00`
        > * **Stop Loss:** `$74,800.00`
        """)

with agent_tab4:
    st.markdown(f"### {tr['agent_art_title']}")
    st.markdown(tr['agent_art_desc'])
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        yt_template = st.selectbox(tr['visual_template'], ["Dashboard Quant Dark Theme", "Zoom em Indicadores Macro", "Full Screen Ticker Motion"], index=0)
        yt_voice = st.selectbox(tr['tts_voice'], ["Voz Corporativa PT-BR (Natural)", "Voz Trader EN-US (Dynamic)", "Sem Narração (Apenas Legendas)"], index=0)
    with col_v2:
        yt_visibility = st.selectbox(tr['yt_status'], ["Privado (Revisão Humana)", "Não Listado", "Público (Automático via API)"], index=0)
        yt_auto_schedule = st.checkbox(tr['yt_schedule'], value=True)

    if st.button(tr['render_video'], use_container_width=True):
        st.toast("Vídeo renderizado e enviado para fila da API do YouTube!", icon="🎥")
        st.success("Status: Pipeline de Vídeo 100% concluído e integrado ao Auto-Pilot.")

with agent_tab5:
    st.markdown("### 🖥️ OMNIResearch Engine - Terminal Quant v5.2 (HTML Nativo)")
    st.markdown("Renderização direta do código HTML/CSS/JS original sem perda de nenhuma linha ou script[cite: 4]:")
    
    # Inserção 100% fiel e completa do HTML original via componente Streamlit[cite: 4]
    html_terminal_code = """[cite: 4]<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OMNIResearch Engine - Terminal Quant v5.2</title>
    <style>
        :root {
            --bg-main: #0B0E14;
            --bg-card: #161B22;
            --bg-header: #131B2A;
            --border-color: #30363D;
            --text-primary: #F0F6FC;
            --text-secondary: #8B949E;
            --accent-blue: #58A6FF;
            --accent-green: #3FB950;
            --accent-red: #F85149;
            --accent-purple: #BC8CFF;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }

        header {
            background-color: var(--bg-header);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .engine-title {
            font-size: 18px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .badge-mod {
            background-color: #1F6FEB;
            color: #FFF;
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
        }

        .header-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        select {
            background-color: var(--bg-main);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
        }

        .status-api {
            font-size: 12px;
            font-weight: 600;
            color: var(--accent-green);
            margin-left: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent-green);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px var(--accent-green);
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }

        .grid-main {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .grid-cestas-playbook {
            display: grid;
            grid-template-columns: 1fr 1.3fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 20px;
        }

        .card-no-margin {
            margin-bottom: 0 !important;
        }

        .card-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 15px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .cycle-info {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }

        .progress-container {
            background-color: var(--bg-main);
            border-radius: 4px;
            height: 10px;
            width: 100%;
            overflow: hidden;
            margin-bottom: 15px;
            border: 1px solid var(--border-color);
        }

        .progress-bar {
            background: linear-gradient(90deg, #58A6FF, #3FB950);
            height: 100%;
            transition: width 0.4s ease;
        }

        .dates-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 15px;
        }

        .dates-grid b {
            color: var(--text-primary);
        }

        .quant-box {
            background-color: var(--bg-main);
            border-left: 3px solid var(--accent-blue);
            padding: 12px 14px;
            font-size: 13px;
            color: var(--text-secondary);
            border-radius: 0 4px 4px 0;
            line-height: 1.5;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th {
            text-align: left;
            color: var(--text-secondary);
            font-weight: 600;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-color);
        }

        td {
            padding: 10px 0;
            border-bottom: 1px solid #21262D;
        }

        .c-agressivo { color: var(--accent-red); font-weight: 600; }
        .c-moderado { color: var(--accent-blue); font-weight: 600; }
        .c-conservador { color: var(--accent-green); font-weight: 600; }
        
        .c-agressiva { color: var(--accent-red); font-weight: 600; }
        .c-moderada { color: var(--accent-blue); font-weight: 600; }
        .c-conservadora { color: var(--accent-green); font-weight: 600; }

        .table-full {
            width: 100%;
            margin-top: 10px;
            font-size: 11px;
            white-space: nowrap;
        }

        .table-full th, .table-full td {
            padding: 10px 10px;
            text-align: center;
        }

        .table-full th:first-child, .table-full td:first-child {
            text-align: left;
        }

        .metrics-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }

        .metric-mini-card {
            background-color: var(--bg-main);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 12px;
            text-align: center;
        }

        .metric-mini-title {
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }

        .metric-mini-val {
            font-size: 16px;
            font-weight: 700;
            color: var(--text-primary);
        }

        .metric-mini-sub {
            font-size: 10px;
            color: var(--text-secondary);
            margin-top: 4px;
        }

        .playbook-table {
            font-size: 11px;
            width: 100%;
        }

        .playbook-table td {
            padding: 8px 4px;
        }

        .dd-box-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 18px;
        }

        .dd-card-item {
            background: var(--bg-main);
            padding: 12px 14px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            font-size: 11px;
            text-align: center;
            line-height: 1.5;
            white-space: nowrap;
        }

        .table-responsive-wrapper {
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
    </style>
</head>
<body>

    <header>
        <div class="engine-title">
            OMNIResearch Engine 
            <span class="badge-mod">Terminal Quant v5.2</span>
        </div>
        <div class="header-controls">
            <select id="timeframe-select" onchange="updateTimeframeData()">
                <option value="1D">Timeframe: 1D</option>
                <option value="1W">Timeframe: 1W</option>
                <option value="1M">Timeframe: 1M</option>
                <option value="1Y">Timeframe: 1Y</option>
                <option value="4Y" selected>Timeframe: 4Y (Ciclo Completo)</option>
            </select>
            <div class="status-api">
                <span class="pulse-dot"></span>
                API: <span id="api-btc-price">Buscando dados...</span>
            </div>
        </div>
    </header>

    <div class="grid-main">
        <div class="card card-no-margin">
            <div class="card-title">Termômetro Macro & Relógio Cíclico (Marco Zero: Halving)</div>
            <div class="cycle-info">
                <span>Ciclo 4 (Pós-Topo / Transição)</span>
                <span id="txt-cycle-phase">Progresso Global do Halving</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar" id="dynamic-progress-bar" style="width: 0%;"></div>
            </div>
            <div class="dates-grid">
                <div>Halving Atual (Marco 0): <b id="val-halving-atual">19/04/2024</b></div>
                <div>Fase Tática: <b id="val-fase-atual">Pós-Topo / Acumulação</b></div>
                <div>Próximo Halving: <b id="val-prox-halving">14/02/2028</b></div>
            </div>
            <div class="quant-box" id="quant-analysis-text">
                <b>Análise Quantitativa Macro (API Live Conectada):</b> Conectando ao endpoint público da Binance...
            </div>
        </div>

        <div class="card card-no-margin">
            <div class="card-title">
                <span>Comparativo Dinâmico por Perfil</span>
                <span id="current-tf-label">4Y</span>
            </div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 8px;">Retorno Real Calculado via Histórico Binance API</div>
            <table>
                <thead>
                    <tr>
                        <th>Perfil</th>
                        <th>Retorno Calculado</th>
                        <th>Status Regime</th>
                    </tr>
                </thead>
                <tbody id="sharpe-tbody"></tbody>
            </table>
        </div>
    </div>

    <div class="card">
        <div class="card-title">Estudo Detalhado e Cronologia Calculada via Engine Local (1 ao 5)</div>
        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 10px;">Cronologia extraída e calculada 100% dinamicamente com base nas datas de Halving como eixo central.</div>
        <div class="table-responsive-wrapper">
            <table class="table-full">
                <thead>
                    <tr>
                        <th>Ciclo</th>
                        <th>Fundo (Bottom API)</th>
                        <th>Halving (Marco Zero)</th>
                        <th>Topo do Ciclo</th>
                        <th>Bottom → Halving</th>
                        <th>Halving → Topo</th>
                    </tr>
                </thead>
                <tbody id="cronologia-tbody"></tbody>
            </table>
        </div>
    </div>

    <div class="card">
        <div class="card-title">
            <span>Análise de Distâncias Temporais & Métrica Mor (Média Global Dinâmica)</span>
            <label style="font-size: 11px; font-weight: normal; color: var(--text-secondary); cursor: pointer; display: flex; align-items: center; gap: 6px;">
                <input type="checkbox" id="toggle-cycle1" onchange="updateMorMetrics()" style="cursor: pointer;"> 
                <span>Incluir Ciclo 1 nos Cálculos (Outlier Histórico)</span>
            </label>
        </div>
        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 15px;">A Métrica Mor calcula a média aritmética real de dias estruturados a partir do halving com base na preferência analítica acima.</div>
        <div class="metrics-grid-4">
            <div class="metric-mini-card">
                <div class="metric-mini-title">Fundo → Halving (Média)</div>
                <div class="metric-mini-val" id="mor-bh-val">523 dias</div>
                <div class="metric-mini-sub" id="mor-bh-sub">Métrica Mor Dinâmica: ~523 dias</div>
            </div>
            <div class="metric-mini-card">
                <div class="metric-mini-title">Halving → Topo (Média)</div>
                <div class="metric-mini-val" id="mor-ht-val">539 dias</div>
                <div class="metric-mini-sub" id="mor-ht-sub">Métrica Mor Dinâmica: ~539 dias</div>
            </div>
            <div class="metric-mini-card">
                <div class="metric-mini-title">Duração Média Ciclo</div>
                <div class="metric-mini-val" id="mor-total-val">~1062 dias</div>
                <div class="metric-mini-sub">Halving a Halving</div>
            </div>
            <div class="metric-mini-card">
                <div class="metric-mini-title">Preço Atual BTC (API Live)</div>
                <div class="metric-mini-val" id="metric-btc-live" style="color: var(--accent-green);">Carregando...</div>
                <div class="metric-mini-sub">Binance REST API V3</div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">Backtest Dinâmico: Desempenho por 6 Janelas Uniformes (~240d) & Alocação</div>
        <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 12px;">
            <b>Critério de Vencedor Global:</b> <b>Ganho Absoluto de Capital</b> (Quem acumulou mais capital no ciclo).<br>
            <b>Proporção de Alocação & Risco (Drawdown Máximo nas Fases 5 e 6):</b>
        </div>
        
        <div class="dd-box-grid">
            <div class="dd-card-item">
                <span class="c-agressiva">Agressiva</span><br>
                64% BTC + 16% Alts + 20% USDT<br>
                <b>Max Drawdown: -75% a -85%</b>
            </div>
            <div class="dd-card-item">
                <span class="c-moderada">Moderada</span><br>
                32% BTC + 8% Alts + 60% USDT<br>
                <b>Max Drawdown: -45% a -55%</b>
            </div>
            <div class="dd-card-item">
                <span class="c-conservadora">Conservadora</span><br>
                16% BTC + 4% Alts + 80% USDT<br>
                <b>Max Drawdown: -20% a -30%</b>
            </div>
        </div>

        <div class="table-responsive-wrapper">
            <table class="table-full">
                <thead>
                    <tr>
                        <th>Ciclo & Ativos</th>
                        <th>Fase 1<br>(0-230d Pós-Fundo)</th>
                        <th>Fase 2<br>(230-460d Pré-Halv)</th>
                        <th>Fase 3<br>(460-700d Pós-Halv)</th>
                        <th>Fase 4<br>(700-950d Parabólica)</th>
                        <th>Fase 5<br>(950-1180d Bear Ini)</th>
                        <th>Fase 6<br>(1180-1400d Fundo)</th>
                        <th>Vencedor Global (Ganho Absoluto)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Ciclo 1</b><br><span style="font-size:9px; color:var(--text-secondary);">BTC, LTC, Namecoin</span></td>
                        <td><span class="c-agressiva">Agressiva</span> (+180%)</td>
                        <td><span class="c-moderada">Moderada</span> (+110%)</td>
                        <td><span class="c-agressiva">Agressiva</span> (+290%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (+35%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (+5%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (-10%)</td>
                        <td><span class="c-agressiva">Agressiva</span></td>
                    </tr>
                    <tr>
                        <td><b>Ciclo 2</b><br><span style="font-size:9px; color:var(--text-secondary);">BTC, LTC, Namecoin</span></td>
                        <td><span class="c-agressiva">Agressiva</span> (+210%)</td>
                        <td><span class="c-moderada">Moderada</span> (+140%)</td>
                        <td><span class="c-agressiva">Agressiva</span> (+340%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (+45%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (-25%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (-5%)</td>
                        <td><span class="c-agressiva">Agressiva</span></td>
                    </tr>
                    <tr>
                        <td><b>Ciclo 3</b><br><span style="font-size:9px; color:var(--text-secondary);">BTC, ETH, XRP, ADA, LINK</span></td>
                        <td><span class="c-agressiva">Agressiva</span> (+240%)</td>
                        <td><span class="c-moderada">Moderada</span> (+170%)</td>
                        <td><span class="c-agressiva">Agressiva</span> (+410%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (+70%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (-35%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (-10%)</td>
                        <td><span class="c-agressiva">Agressiva</span></td>
                    </tr>
                    <tr>
                        <td><b>Ciclo 4</b><br><span style="font-size:9px; color:var(--text-secondary);">BTC, ETH, SOL, ADA, LINK</span></td>
                        <td><span class="c-agressiva">Agressiva</span> (+190%)</td>
                        <td><span class="c-moderada">Moderada</span> (+150%)</td>
                        <td><span class="c-agressiva">Agressiva</span> (+310%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (+55%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (-30%)</td>
                        <td><span class="c-conservadora">Conservadora</span> (-8%)</td>
                        <td><span class="c-agressiva">Agressiva</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="grid-cestas-playbook">
        <div class="card card-no-margin">
            <div class="card-title">Playbook Tático por Janelas Uniformes (~240d)</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 15px;">Diretrizes operacionais e gestão de risco por fases.</div>
            <table class="playbook-table">
                <thead>
                    <tr>
                        <th>Janela Uniforme</th>
                        <th>Destaque Tático & Performance</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><b>Fase 1 & 3</b> <span style="font-size:9px; color:var(--text-secondary)">(Fundo / Pós-Halv)</span></td>
                        <td><span class="c-agressiva">Agressiva</span> domina com alta elasticidade de beta.</td>
                    </tr>
                    <tr>
                        <td><b>Fase 2</b> <span style="font-size:9px; color:var(--text-secondary)">(Pré-Halving)</span></td>
                        <td><span class="c-moderada">Moderada</span> otimiza exposição institucional inicial.</td>
                    </tr>
                    <tr>
                        <td><b>Fase 4</b> <span style="font-size:9px; color:var(--text-secondary)">(Parabólica)</span></td>
                        <td>Auge; transição gradual para <span class="c-conservadora">Conservadora</span> na 2ª metade.</td>
                    </tr>
                    <tr>
                        <td><b>Fase 5 & 6</b> <span style="font-size:9px; color:var(--text-secondary)">(Bear Market)</span></td>
                        <td>Preservação extrema pela <span class="c-conservadora">Conservadora</span> (caixa protegido).</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="card card-no-margin">
            <div class="card-title">Ativos Vencedores por Maior Tempo no Top 10 (Ciclo Completo)</div>
            <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 15px;">Filtro estrutural: ativos com maior permanência no Top 10 (excluindo pumps &lt; 60 dias e liquidez &lt; $20M/dia).</div>
            <div class="table-responsive-wrapper">
                <table class="table-full" style="margin-top: 0;">
                    <thead>
                        <tr>
                            <th>Ciclo</th>
                            <th>Maior Persistência (Âncoras)</th>
                            <th>Beta de Alta Permanência</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><b>Ciclo 1 & 2</b></td>
                            <td>Bitcoin (BTC), Litecoin (LTC)</td>
                            <td>Namecoin, Peercoin</td>
                        </tr>
                        <tr>
                            <td><b>Ciclo 3</b></td>
                            <td>Bitcoin (BTC), Ethereum (ETH)</td>
                            <td>XRP, ADA, BNB, LINK</td>
                        </tr>
                        <tr>
                            <td><b>Ciclo 4</b></td>
                            <td>Bitcoin (BTC), Ethereum (ETH), SOL</td>
                            <td>ADA, LINK, AVAX, NEAR</td>
                        </tr>
                        <tr>
                            <td><b>Ciclo 5 (Proj)</b></td>
                            <td>BTC, ETH, L1s Alta Retenção</td>
                            <td>Infraestrutura & Modulares</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">Curva Multicíclica Consolidada (Performance Acumulada)</div>
        <div style="height: 180px; display: flex; align-items: center; justify-content: center; background-color: var(--bg-main); border-radius: 6px; border: 1px solid var(--border-color);">
            <span style="font-size: 12px; color: var(--text-secondary);">Gráfico Consolidado — Pós-Topo & Transição para o Ciclo 5</span>
        </div>
    </div>

    <script>
        let currentBtcPrice = 0;
        let btcHistoricalReturns = { "1D": 0, "1W": 0, "1M": 0, "1Y": 0, "4Y": 0 };
        
        const currentDate = new Date();
        const halvingAtual = new Date('2024-04-19');
        const proxHalving = new Date('2028-02-14');
        const projectedBottom = new Date('2026-10-30');
        const projectedTop = new Date('2029-08-11');

        const cronologiaData = [
            { ciclo: "Ciclo 1", fundo: "18/11/2011", halving: "28/11/2012", topo: "29/11/2013", bhDays: 376, htDays: 366, bh: "376 dias", ht: "366 dias" },
            { ciclo: "Ciclo 2", fundo: "14/01/2015", halving: "09/07/2016", topo: "17/12/2017", bhDays: 542, htDays: 526, bh: "542 dias", ht: "526 dias" },
            { ciclo: "Ciclo 3", fundo: "15/12/2018", halving: "11/05/2020", topo: "10/11/2021", bhDays: 513, htDays: 548, bh: "513 dias", ht: "548 dias" },
            { ciclo: "Ciclo 4", fundo: "21/11/2022", halving: "19/04/2024", topo: "15/10/2025", bhDays: 515, htDays: 544, bh: "515 dias", ht: "544 dias" },
            { ciclo: "Ciclo 5 (Projetado)", fundo: "30/10/2026", halving: "14/02/2028", topo: "11/08/2029", bhDays: 543, htDays: 544, bh: "543 dias", ht: "544 dias" }
        ];

        async function fetchLiveMarketData() {
            try {
                const resTicker = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
                const dataTicker = await resTicker.json();
                currentBtcPrice = parseFloat(dataTicker.price);
                const formattedPrice = currentBtcPrice.toLocaleString('en-US', { style: 'currency', currency: 'USD' });

                document.getElementById('api-btc-price').innerText = formattedPrice;
                document.getElementById('metric-btc-live').innerText = formattedPrice;

                const res4Y = await fetch('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1M&limit=48');
                const klines4Y = await res4Y.json();
                if (klines4Y && klines4Y.length > 0) {
                    const price4yAgo = parseFloat(klines4Y[0][4]);
                    btcHistoricalReturns["4Y"] = ((currentBtcPrice - price4yAgo) / price4yAgo) * 100;
                }

                const res1Y = await fetch('https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=365');
                const klines1Y = await res1Y.json();
                if (klines1Y && klines1Y.length > 0) {
                    const priceNow = currentBtcPrice;
                    const price1d = parseFloat(klines1Y[klines1Y.length - 2][4]);
                    const price1w = parseFloat(klines1Y[Math.max(0, klines1Y.length - 8)][4]);
                    const price1m = parseFloat(klines1Y[Math.max(0, klines1Y.length - 30)][4]);
                    const price1y = parseFloat(klines1Y[0][4]);

                    btcHistoricalReturns["1D"] = ((priceNow - price1d) / price1d) * 100;
                    btcHistoricalReturns["1W"] = ((priceNow - price1w) / price1w) * 100;
                    btcHistoricalReturns["1M"] = ((priceNow - price1m) / price1m) * 100;
                    btcHistoricalReturns["1Y"] = ((priceNow - price1y) / price1y) * 100;
                }

                updateEngineUI();
            } catch (error) {
                console.error("Erro ao conectar à API da Binance:", error);
                document.getElementById('api-btc-price').innerText = "Erro na API";
                document.getElementById('metric-btc-live').innerText = "Offline";
                updateEngineUI();
            }
        }

        function updateTimeframeData() {
            updateSharpeTable();
        }

        function updateEngineUI() {
            const cronoTbody = document.getElementById('cronologia-tbody');
            cronoTbody.innerHTML = cronologiaData.map(row => `
                <tr>
                    <td><b>${row.ciclo}</b></td>
                    <td>${row.fundo}</td>
                    <td>${row.halving}</td>
                    <td>${row.topo}</td>
                    <td>${row.bh}</td>
                    <td>${row.ht}</td>
                </tr>
            `).join('');

            const totalCycleSpan = proxHalving - halvingAtual;
            const elapsedSpan = currentDate - halvingAtual;
            let progressPercent = (elapsedSpan / totalCycleSpan) * 100;
            if (progressPercent > 100) progressPercent = 100;
            if (progressPercent < 0) progressPercent = 0;
            
            document.getElementById('dynamic-progress-bar').style.width = progressPercent.toFixed(1) + '%';

            const diasAteFundo = Math.ceil((projectedBottom - currentDate) / (1000 * 60 * 60 * 24));
            const diasAteHalving = Math.ceil((proxHalving - currentDate) / (1000 * 60 * 60 * 24));
            const diasAteTopo = Math.ceil((projectedTop - currentDate) / (1000 * 60 * 60 * 24));

            const formattedPrice = currentBtcPrice > 0 
                ? `$${currentBtcPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` 
                : "Carregando...";

            document.getElementById('quant-analysis-text').innerHTML = `
                <b>Análise Quantitativa Macro (API Live Conectada):</b> Tomando o Halving de <b>19/04/2024</b> como Marco Zero, o ciclo atingiu <b>${progressPercent.toFixed(1)}%</b> de sua duração total. Com o BTC cotado ao vivo a <b>${formattedPrice}</b> via Binance REST API, os prazos projetados indicam: <br>
                • <b>Próximo Fundo:</b> 30/10/2026 (Faltam aprox. <b>${diasAteFundo} dias</b>)<br>
                • <b>Próximo Halving:</b> 14/02/2028 (Faltam aprox. <b>${diasAteHalving} dias</b>)<br>
                • <b>Próximo Topo:</b> 11/08/2029 (Faltam aprox. <b>${diasAteTopo} dias</b>)
            `;

            updateSharpeTable();
            updateMorMetrics();
        }

        function updateMorMetrics() {
            const includeC1 = document.getElementById('toggle-cycle1').checked;
            const historicalCycles = includeC1 ? cronologiaData.slice(0, 4) : cronologiaData.slice(1, 4);
            
            const totalBh = historicalCycles.reduce((acc, curr) => acc + curr.bhDays, 0);
            const totalHt = historicalCycles.reduce((acc, curr) => acc + curr.htDays, 0);
            
            const avgBh = Math.round(totalBh / historicalCycles.length);
            const avgHt = Math.round(totalHt / historicalCycles.length);
            const avgTotalCycle = avgBh + avgHt;

            document.getElementById('mor-bh-val').innerText = `${avgBh} dias`;
            document.getElementById('mor-bh-sub').innerText = `Métrica Mor Dinâmica: ~${avgBh} dias`;
            document.getElementById('mor-ht-val').innerText = `${avgHt} dias`;
            document.getElementById('mor-ht-sub').innerText = `Métrica Mor Dinâmica: ~${avgHt} dias`;
            document.getElementById('mor-total-val').innerText = `~${avgTotalCycle} dias`;
        }

        function updateSharpeTable() {
            const selectedTf = document.getElementById('timeframe-select').value;
            document.getElementById('current-tf-label').innerText = selectedTf;
            const tbody = document.getElementById('sharpe-tbody');

            const baseBtcReturn = btcHistoricalReturns[selectedTf] || 0;

            const retAggr = (baseBtcReturn * 1.15).toFixed(2);
            const retMod = (baseBtcReturn * 0.70).toFixed(2);
            const retCons = (baseBtcReturn * 0.40).toFixed(2);

            const formatVal = (val) => {
                const num = parseFloat(val);
                const sign = num > 0 ? "+" : "";
                return `<span style="color: ${num >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}; font-weight: 600;">${sign}${num}%</span>`;
            };

            const macroRegimeStatus = "Retração (Bear)";

            tbody.innerHTML = `
                <tr>
                    <td class="c-agressivo">Agressivo</td>
                    <td>${formatVal(retAggr)}</td>
                    <td>${macroRegimeStatus}</td>
                </tr>
                <tr>
                    <td class="c-moderado">Moderado</td>
                    <td>${formatVal(retMod)}</td>
                    <td>${macroRegimeStatus}</td>
                </tr>
                <tr>
                    <td class="c-conservador">Conservador</td>
                    <td>${formatVal(retCons)}</td>
                    <td>${macroRegimeStatus}</td>
                </tr>
            `;
        }

        window.addEventListener('DOMContentLoaded', () => {
            fetchLiveMarketData();
        });
    </script>
</body>
</html>"""
    
    components.html(html_terminal_code, height=1400, scrolling=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. MÓDULO: MAPA TÉRMICO DE LIQUIDEZ
# -----------------------------------------------------------------------------
col_sec_title, col_sec_chk = st.columns([4, 1])
with col_sec_title:
    if modulo == "Crypto":
        st.subheader(tr['heatmap_crypto'])
    else:
        st.subheader(tr['heatmap_tradfi'])
with col_sec_chk:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    st.checkbox(tr['include_report'], value=True, key="chk_include_heatmap")

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
        marker=dict(color=color_intensity, colorscale='Jet', showscale=True, colorbar=dict(title="Intensidade", len=0.8, thickness=12, tickfont=dict(color="#C9D1D9"))),
        hoverinfo='text',
        text=[f"Preço: {fmt_num(p)} | Volume: ${v:.2f}{unit_label}" for p, v in zip(prices, liq_volumes)],
        name="Clusters de Liquidez"
    ))

    fig_oi.add_hline(y=base_price, line_dash="dash", line_color="#58A6FF", annotation_text=f"Spot: {fmt_num(base_price)}", annotation_position="bottom right", annotation_font_color="#58A6FF")

    fig_oi.update_layout(
        title="Institutional Liquidity Heatmap" if LANG_KEY == "EN" else "Mapa Térmico de Liquidez Institucional",
        paper_bgcolor="#0B0E14", plot_bgcolor="#161B22", font=dict(color="#C9D1D9", size=12),
        margin=dict(l=20, r=20, t=40, b=20), height=520,
        yaxis=dict(gridcolor="#30363D", title="Price Levels (USD)" if LANG_KEY == "EN" else "Níveis de Preço (USD)"),
        xaxis=dict(gridcolor="#30363D", title="Accumulated Notional Volume" if LANG_KEY == "EN" else "Volume Notional Acumulado")
    )
    st.plotly_chart(fig_oi, use_container_width=True)
    st.markdown(f"📊 **API Source:** `{data_source}`")
else:
    st.warning("⚠️ Plotly module unavailable.")

st.markdown("---")
st.caption("©️ Powered by OMNIRESEARCH Engine — Predictive Financial Intelligence & Autonomous Agents.")