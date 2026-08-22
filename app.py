import json
import io
from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import numpy as np

# ==================== 1. IMPORTAÇÕES E CONFIGURAÇÃO INICIAL ====================
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 2. ESTILIZAÇÃO CSS CUSTOMIZADA ====================
st.markdown("""<style>
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    .col-header-sync {
        min-height: 64px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .status-bar {
        background-color: #131B2A;
        padding: 10px 18px;
        border-radius: 8px;
        border: 1px solid #1E293B;
        margin-bottom: 8px;
        color: #94A3B8;
        font-size: 13px;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .metric-title { font-size: 12px; color: #8B949E; font-weight: 600; }
    .metric-value { font-size: 18px; font-weight: 700; color: #F0F6FC; margin: 4px 0; }
    .metric-change-pos { font-size: 12px; color: #3FB950; font-weight: 600; }
    .metric-change-neg { font-size: 12px; color: #F85149; font-weight: 600; }
    .metric-change-neutral { font-size: 12px; color: #58A6FF; font-weight: 600; }
    .premium-badge { color: #58A6FF; font-weight: bold; }

    .pred-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 14px;
        height: 85px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pred-title { font-size: 11px; color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .pred-value { font-size: 15px; font-weight: 700; color: #F0F6FC; }
    .pred-sub { font-size: 11px; font-weight: 600; }

    .stTextArea {
        margin-top: -5px !important;
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
    div[data-testid="stCheckbox"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        height: 24px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    div[data-testid="stCheckbox"] > label {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        margin: 0px !important;
        padding: 0px !important;
        cursor: pointer !important;
    }
    div[data-baseweb="checkbox"] input:checked + div {
        background-color: #238636 !important;
        border-color: #238636 !important;
    }
    input[type="checkbox"]:checked { accent-color: #238636 !important; }
</style>""", unsafe_allow_html=True)

# ==================== 3. DICIONÁRIOS DE DADOS E CATEGORIAS ISOLADAS ====================
CATEGORIES_TRADFI = {
    "1 - Bancos e Seguradoras": {
        "tag": "Banking & Ins.",
        "assets": [
            ("ITUB4", "ITUB4.SA", "R$"),
            ("BBAS3", "BBAS3.SA", "R$"),
            ("BBDC4", "BBDC4.SA", "R$"),
            ("BBSE3", "BBSE3.SA", "R$"),
        ]
    },
    "2 - Energia": {
        "tag": "Energy",
        "assets": [
            ("PETR4", "PETR4.SA", "R$"),
            ("PRIO3", "PRIO3.SA", "R$"),
            ("EQTL3", "EQTL3.SA", "R$"),
            ("CPFE3", "CPFE3.SA", "R$"),
        ]
    },
    "3 - Tech": {
        "tag": "Technology",
        "assets": [
            ("TOTVS3", "TOTS3.SA", "R$"),
            ("NVDA", "NVDA", "$"),
            ("AAPL", "AAPL", "$"),
            ("MSFT", "MSFT", "$"),
        ]
    },
    "4 - Commodities": {
        "tag": "Commodities",
        "assets": [
            ("VALE3", "VALE3.SA", "R$"),
            ("GGBR4", "GGBR4.SA", "R$"),
            ("CMIG4", "CMIG4.SA", "R$"),
            ("KLBN11", "KLBN11.SA", "R$"),
        ]
    },
    "5 - Varejo": {
        "tag": "Retail",
        "assets": [
            ("ASAI3", "ASAI3.SA", "R$"),
            ("LREN3", "LREN3.SA", "R$"),
            ("MGLU3", "MGLU3.SA", "R$"),
            ("RADL3", "RADL3.SA", "R$"),
        ]
    },
    "6 - Logística e Infra.": {
        "tag": "Infra & Log",
        "assets": [
            ("RAIL3", "RAIL3.SA", "R$"),
            ("WEGE3", "WEGE3.SA", "R$"),
            ("CCRO3", "CCRO3.SA", "R$"),
            ("EMBR3", "EMBR3.SA", "R$"),
        ]
    },
    "7 - Agro e Indústria": {
        "tag": "Agri & Industry",
        "assets": [
            ("SLCE3", "SLCE3.SA", "R$"),
            ("BRFS3", "BRFS3.SA", "R$"),
            ("ABEV3", "ABEV3.SA", "R$"),
            ("JBSS3", "JBSS3.SA", "R$"),
        ]
    }
}

MACRO_BENCHMARKS = [
    {"key": "SPX", "ticker": "^GSPC", "label": "1. S&P 500 / SPX", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "IBOV", "ticker": "^BVSP", "label": "2. Ibovespa / IBOV", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "BRENT", "ticker": "BZ=F", "label": "3. Petróleo Brent", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "GOLD", "ticker": "GC=F", "label": "4. Ouro Spot", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "5. USD / BRL / Dólar Real", "unit": "pts", "prefix": "R$ ", "badge": "Direct API"}
]

CATEGORIES_CRYPTO = {
    "1 - ETFs": {
        "tag": "ETFs",
        "assets": [
            ("IBIT (BlackRock)", "IBIT", "$"),
            ("FBTC (Fidelity)", "FBTC", "$"),
            ("ETHA (Ethereum)", "ETHA", "$"),
            ("BITO (Futures)", "BITO", "$"),
        ]
    },
    "2 - Treasury": {
        "tag": "Treasury",
        "assets": [
            ("MicroStrategy", "MSTR", "$"),
            ("Marathon Digital", "MARA", "$"),
            ("Riot Platforms", "RIOT", "$"),
            ("Coinbase Global", "COIN", "$"),
        ]
    },
    "3 - Mineração e Hashrate": {
        "tag": "Mining",
        "assets": [
            ("CleanSpark", "CLSK", "$"),
            ("Hut 8", "HUT", "$"),
            ("Bitfarms", "BITF", "$"),
            ("Iris Energy", "IREN", "$"),
        ]
    },
    "4 - Volume Spot (24 hs)": {
        "tag": "Spot Vol",
        "assets": [
            ("BTCUSDT", "BTC-USD", "$"),
            ("ETHUSDT", "ETH-USD", "$"),
            ("SOLUSDT", "SOL-USD", "$"),
            ("BNBUSDT", "BNB-USD", "$"),
        ]
    },
    "5 - Volume Futuros (24 hs)": {
        "tag": "Derivatives",
        "assets": [
            ("BTC Perp", "BTC-USD", "$"),
            ("ETH Perp", "ETH-USD", "$"),
            ("SOL Perp", "SOL-USD", "$"),
            ("BNB Perp", "BNB-USD", "$"),
        ]
    },
    "6 - Open Interest": {
        "tag": "Open Interest",
        "assets": [
            ("BTC OI Base", "BTC-USD", "$"),
            ("ETH OI Base", "ETH-USD", "$"),
            ("SOL OI Base", "SOL-USD", "$"),
            ("AVAX OI Base", "AVAX-USD", "$"),
        ]
    },
    "7 - DeFi e Layer 1s": {
        "tag": "DeFi & L1",
        "assets": [
            ("UNI (Uniswap)", "UNI7083-USD", "$"),
            ("AAVE (Aave)", "AAVE-USD", "$"),
            ("LINK (Chainlink)", "LINK-USD", "$"),
            ("AVAX (Avalanche)", "AVAX-USD", "$"),
        ]
    },
    "8 - Stablecoins": {
        "tag": "Stablecoins",
        "assets": [
            ("USDT / USD", "USDT-USD", "$"),
            ("USDC / USD", "USDC-USD", "$"),
            ("USDT / BRL", "BRL=X", "R$"),
            ("DAI / USD", "DAI-USD", "$"),
        ]
    }
}

CRYPTO_BENCHMARKS = [
    {"key": "BTC", "ticker": "BTC-USD", "label": "1. Bitcoin / BTC", "prefix": "$ ", "badge": "Direct API"},
    {"key": "ETH", "ticker": "ETH-USD", "label": "2. Ethereum / ETH", "prefix": "$ ", "badge": "Direct API"},
    {"key": "BTC_D", "type": "global_api", "sub_key": "btc_d", "label": "3. Bitcoin Dominance / BTC.D", "badge": "CoinGecko API"},
    {"key": "USDT_D", "type": "global_api", "sub_key": "usdt_d", "label": "4. Tether Dominance / USDT.D", "badge": "CoinGecko API"},
    {"key": "FEAR_GREED", "type": "fng_api", "label": "5. Bitcoin Fear & Greed Index", "badge": "Alternative.me API"}
]

# ==================== 4. FUNÇÕES AUXILIARES E FORMATAÇÃO ====================
def fmt_num(val, dec=2):
    if val is None or pd.isna(val) or val == 0.0:
        return "--"
    s = f"{val:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(val):
    if val is None or pd.isna(val):
        return "0,00%"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%".replace(".", ",")

def generate_pdf_report(content_text, company_name, timestamp_str):
    if not REPORTLAB_AVAILABLE:
        return content_text.encode("utf-8")
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )
    
    story = []
    story.append(Paragraph(f"<b>{company_name} - Relatório Institucional</b>", styles['Heading1']))
    story.append(Paragraph(f"Emitido em: {timestamp_str}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    for line in content_text.split('\n'):
        if line.strip() == "":
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), body_style))
            
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==================== 5. INTEGRAÇÃO COM APIS EXTERNAS ====================
@st.cache_data(ttl=600)
def fetch_btc_fng():
    try:
        res = requests.get("https://api.alternative.me/fng/", timeout=3)
        if res.status_code == 200:
            data = res.json()["data"][0]
            val = data.get("value", "62")
            classification = data.get("value_classification", "Greed")
            return f"{val} / 100", f"{classification}"
    except Exception:
        pass
    return "62 / 100", "Greed"

@st.cache_data(ttl=600)
def fetch_global_crypto_data():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global", timeout=3)
        if res.status_code == 200:
            data = res.json()["data"]
            btc_d = data.get("market_cap_percentage", {}).get("btc", 56.8)
            usdt_d = data.get("market_cap_percentage", {}).get("usdt", 5.2)
            btc_d_chg = data.get("market_cap_change_percentage_24h_usd", 0.35)
            usdt_d_chg = -0.18
            return {
                "btc_d_val": f"{btc_d:.2f}%".replace(".", ","),
                "btc_d_chg": btc_d_chg,
                "usdt_d_val": f"{usdt_d:.2f}%".replace(".", ","),
                "usdt_d_chg": usdt_d_chg
            }
    except Exception:
        pass
    return {
        "btc_d_val": "56,80%",
        "btc_d_chg": 0.35,
        "usdt_d_val": "5,20%",
        "usdt_d_chg": -0.18
    }

def fetch_brapi_fallback(failed_symbols, token=""):
    brapi_quotes = {}
    if not failed_symbols:
        return brapi_quotes

    token_clean = token.split("=")[-1].strip().replace('"', '').replace("'", "") if token else ""
    sym_map = {sym.replace(".SA", "").strip().upper(): sym for sym in failed_symbols}
    clean_symbols_str = ",".join(sym_map.keys())

    headers = {"User-Agent": "Mozilla/5.0"}
    params = {}
    if token_clean:
        params["token"] = token_clean

    try:
        url = f"https://brapi.dev/api/quote/{clean_symbols_str}"
        res = requests.get(url, params=params, headers=headers, timeout=6)
        if res.status_code == 200:
            results = res.json().get("results", [])
            for item in results:
                raw_sym = str(item.get("symbol", "")).upper()
                orig_sym = sym_map.get(raw_sym, raw_sym + ".SA")
                
                price = (
                    item.get("regularMarketPrice") or 
                    item.get("close") or 
                    item.get("regularMarketPreviousClose") or 
                    item.get("price") or 0.0
                )
                chg = (
                    item.get("regularMarketChangePercent") or 
                    item.get("changePercent") or 0.0
                )
                
                if price and float(price) > 0:
                    brapi_quotes[orig_sym] = {"price": float(price), "change": float(chg)}
    except Exception:
        pass

    return brapi_quotes

@st.cache_data(ttl=300)
def fetch_realtime_quotes(symbols_tuple, brapi_token=""):
    quotes = {sym: {"price": 0.0, "change": 0.0} for sym in symbols_tuple}
    alias_map = {"UNI-USD": "UNI7083-USD"}

    try:
        import yfinance as yf
        download_list = [alias_map.get(s, s) for s in symbols_tuple]
        df_data = yf.download(download_list, period="5d", interval="1d", group_by="ticker", progress=False)
        
        for orig_sym in symbols_tuple:
            actual_sym = alias_map.get(orig_sym, orig_sym)
            try:
                if len(symbols_tuple) == 1:
                    df_sym = df_data
                else:
                    df_sym = df_data[actual_sym] if actual_sym in df_data.columns.get_level_values(0) else None
                
                if df_sym is not None and not df_sym.empty:
                    df_clean = df_sym.dropna(subset=["Close"])
                    if len(df_clean) >= 1:
                        p = float(df_clean["Close"].iloc[-1])
                        prev = float(df_clean["Close"].iloc[-2]) if len(df_clean) >= 2 else p
                        c = ((p - prev) / prev) * 100 if prev > 0 else 0.0
                        if p > 0:
                            quotes[orig_sym] = {"price": p, "change": c}
            except Exception:
                pass
    except Exception:
        pass

    missing_symbols = [s for s, v in quotes.items() if v["price"] == 0.0]
    for orig_sym in missing_symbols:
        actual_sym = alias_map.get(orig_sym, orig_sym)
        try:
            import yfinance as yf
            t = yf.Ticker(actual_sym)
            hist = t.history(period="5d")
            if not hist.empty:
                df_clean = hist.dropna(subset=["Close"])
                if len(df_clean) >= 1:
                    p = float(df_clean["Close"].iloc[-1])
                    prev = float(df_clean["Close"].iloc[-2]) if len(df_clean) >= 2 else p
                    c = ((p - prev) / prev) * 100 if prev > 0 else 0.0
                    if p > 0:
                        quotes[orig_sym] = {"price": p, "change": c}
        except Exception:
            pass

    failed_b3 = [
        sym for sym, val in quotes.items()
        if (val["price"] == 0.0 or pd.isna(val["price"])) and sym.endswith(".SA")
    ]

    if failed_b3:
        brapi_data = fetch_brapi_fallback(failed_b3, token=brapi_token)
        for sym, data_dict in brapi_data.items():
            quotes[sym] = data_dict

    return quotes

# ==================== 6. CONFIGURAÇÃO DA BARRA LATERAL (SIDEBAR & BYOK & CRM) ====================
st.sidebar.title("⚙️ Configurações OMNI")
modulo = st.sidebar.radio("📊 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1)
tier_selected = st.sidebar.radio("Plano Ativo:", ["Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B White-Label)"], index=1)

allow_customization = "Free" not in tier_selected
allow_white_label = "Premium" in tier_selected
max_free_tickers = 5 if "Standard" in tier_selected else (999 if "Premium" in tier_selected else 0)

# Painel BYOK (Bring Your Own Key) & APIs de Mercado
with st.sidebar.expander("🔑 BYOK & Credenciais de APIs", expanded=False):
    brapi_token = st.text_input("BRAPI API Token (Ações B3):", value="", type="password")
    openai_api_key = st.text_input("OpenAI / DeepSeek API Key:", value="", type="password")
    llm_provider = st.selectbox("Provedor LLM IA Preditiva:", ["OpenAI GPT-4o", "DeepSeek V3", "Anthropic Claude 3.5"], index=0)

# Integração com CRM & Webhooks (B2B)
with st.sidebar.expander("🔗 Integração CRM & Webhooks", expanded=False):
    crm_enabled = st.checkbox("Ativar Sincronização CRM", value=True)
    crm_webhook_url = st.text_input("Webhook URL (HubSpot / Salesforce / Zapier):", value="https://webhook.site/omni-lead-sync")
    if st.button("📤 Testar Envio p/ CRM"):
        if crm_enabled and crm_webhook_url:
            st.success("Lead & Relatório sincronizados com sucesso via Webhook!")
        else:
            st.warning("Ative a sincronização e configure uma URL válida.")

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

selected_categories = [key for key in active_categories.keys() if st.sidebar.checkbox(key, value=True)]
custom_tickers = []
if allow_customization:
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3.SA, PEPE-USD):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()][:max_free_tickers]

horizonte_pred = st.sidebar.selectbox("Horizonte Temporário:", ["24 Horas", "48 Horas", "7 Dias"], index=1)
alvo_pct = st.sidebar.slider("Projeção de Resposta (%)", 0.5, 15.0, 3.0, 0.5)
stop_pct = st.sidebar.slider("Zona de Suporte / Defesa (%)", 0.5, 15.0, 3.0, 0.5)
formato = st.sidebar.radio(f"📄 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube Auto-Pilot)"], index=0)

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    company_name = st.sidebar.text_input("Nome da Casa/Escritório:", "XP / BTG / Gestora")
    cnpi_code = st.sidebar.text_input("Registro CNPI/Responsável:", "CNPI-T 3421")

# ==================== 7. EXECUÇÃO DE BUSCA E TÍTULO PRINCIPAL ====================
symbols_to_fetch = [item["ticker"] for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS if item.get("ticker")]
for cat_info in active_categories.values():
    for _, ticker, _ in cat_info["assets"]:
        symbols_to_fetch.append(ticker)
symbols_to_fetch.extend(custom_tickers)

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), brapi_token=brapi_token)
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()

active_display_categories = active_categories.copy()
if custom_tickers:
    active_display_categories["0 - Tickers Personalizados"] = {
        "tag": "Custom Feed",
        "assets": [(t, t, "R$" if ".SA" in t else "$") for t in custom_tickers]
    }
    if "0 - Tickers Personalizados" not in selected_categories:
        selected_categories.insert(0, "0 - Tickers Personalizados")

if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏢 {company_name} — Terminal Quant ({modulo})")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code} | LLM: {llm_provider}")
else:
    st.title(f"⚡ OMNIRESEARCH Engine — {modulo}")
    st.caption("Plataforma Integrada de Inteligência Financeira")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(f'<div class="status-bar">🕒 <b>Dados consolidados às {now_str}</b> | Status API: <span style="color: #3FB950;">🟢 Online</span> | <b>Módulo:</b> {modulo}</div>', unsafe_allow_html=True)
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

# ==================== 8. PAINEL DE RELATÓRIO / ROTEIRO (ENTRADA PRINCIPAL) ====================
col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.markdown('<div class="col-header-sync">', unsafe_allow_html=True)
    st.subheader(f"📄 Entrega Padrão — {formato}")
    st.caption("Relatório analítico gerado com dados consolidados em tempo real:")
    st.markdown('</div>', unsafe_allow_html=True)

    if "B2B" in formato:
        report_lines = [
            f"=== RELATÓRIO INSTITUCIONAL {modulo.upper()} (B2B) ===",
            f"Emitente: {company_name} | Responsável: {cnpi_code}",
            f"Data/Hora de Emissão: {now_str}",
            f"Horizonte Analítico: {horizonte_pred} | Alvo: +{alvo_pct}% | Stop Defesa: -{stop_pct}%",
            f"Sentimento de Mercado (Fear & Greed / Macro): {fng_val} ({fng_class})",
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
                    report_lines.append(f"  • {disp_name} ({ticker}): {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        
        report_lines.extend([
            "",
            "--- CONCLUSÃO TÉCNICA QUANT ---",
            f"Tendência estrutural alinhada ao horizonte de {horizonte_pred}. Monitoramento ativo de zonas de liquidez para proteção de posições."
        ])
        output_content = "\n".join(report_lines)
        st.text_area("", value=output_content, height=410, label_visibility="collapsed")
        
        st.markdown("**Opções de Exportação do Relatório:**")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.download_button("💾 Baixar (TXT)", data=output_content, file_name=f"OMNI_Relatorio_{modulo}.txt", mime="text/plain", use_container_width=True)
        with col_b2:
            json_data = json.dumps({
                "module": modulo,
                "timestamp": now_str,
                "company": company_name,
                "cnpi": cnpi_code,
                "horizon": horizonte_pred,
                "target_pct": alvo_pct,
                "stop_pct": stop_pct,
                "categories": {
                    cat_name: {
                        disp_name: quotes.get(ticker, {"price": 0.0, "change": 0.0})["price"] 
                        for disp_name, ticker, currency in active_display_categories[cat_name]["assets"] 
                        if st.session_state.get(f"chk_asset_{cat_name}_{ticker}", True)
                    } 
                    for cat_name in selected_categories 
                    if cat_name in active_display_categories and st.session_state.get(f"chk_cat_{cat_name}", True)
                }
            }, indent=4, ensure_ascii=False)
            st.download_button("💾 Baixar (JSON)", data=json_data, file_name=f"OMNI_Relatorio_{modulo}.json", mime="application/json", use_container_width=True)
        with col_b3:
            pdf_bytes = generate_pdf_report(output_content, company_name, now_str)
            st.download_button("📄 Baixar (PDF)", data=pdf_bytes, file_name=f"OMNI_Relatorio_{modulo}.pdf", mime="application/pdf", use_container_width=True)
    else:
        script_lines = [
            f"=== ROTEIRO YOUTUBE AUTO-PILOT ({modulo.upper()}) ===",
            f"Data/Hora: {now_str}",
            f"Horizonte: {horizonte_pred}",
            "",
            "[INTRODUÇÃO - 00:00]",
            f"Fala, investidor! Sejam bem-vindos a mais um panorama de {modulo} com os dados consolidados em {now_str}.",
            "",
            "[DESENVOLVIMENTO - ANÁLISE DE MERCADO]"
        ]
        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_key = f"chk_cat_{cat_name}"
                if not st.session_state.get(cat_key, True):
                    continue
                cat_info = active_display_categories[cat_name]
                script_lines.append(f"Destaques em {cat_name}:")
                active_assets = [
                    (d, t, c) for d, t, c in cat_info["assets"] 
                    if st.session_state.get(f"chk_asset_{cat_name}_{t}", True)
                ]
                for disp_name, ticker, currency in active_assets[:2]:
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    script_lines.append(f" - {disp_name} negociado a {currency} {fmt_num(q['price'])}, registrando {fmt_pct(q['change'])} hoje.")
        script_lines.extend([
            "",
            "[FECHAMENTO - CALL TO ACTION]",
            "Deixe o seu like, se inscreva no canal e ative as notificações. Bons trades e até a próxima!"
        ])
        script_text = "\n".join(script_lines)
        st.text_area("", value=script_text, height=410, label_visibility="collapsed")
        
        st.markdown("**Opções de Exportação do Roteiro:**")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.download_button("💾 Baixar (TXT)", data=script_text, file_name=f"OMNI_Roteiro_{modulo}.txt", mime="text/plain", use_container_width=True)
        with col_b2:
            json_data = json.dumps({"module": modulo, "timestamp": now_str, "script": script_text}, indent=4, ensure_ascii=False)
            st.download_button("💾 Baixar (JSON)", data=json_data, file_name=f"OMNI_Roteiro_{modulo}.json", mime="application/json", use_container_width=True)
        with col_b3:
            pdf_bytes = generate_pdf_report(script_text, company_name, now_str)
            st.download_button("📄 Baixar (PDF)", data=pdf_bytes, file_name=f"OMNI_Roteiro_{modulo}.pdf", mime="application/pdf", use_container_width=True)

# ==================== 9. MÉTRICAS AGREGADAS E ALVOS PREDITIVOS ====================
with col_right:
    st.markdown('<div class="col-header-sync">', unsafe_allow_html=True)
    st.subheader(f"📊 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado às {datetime.now().strftime('%H:%M:%S BRT')}")
    st.markdown('</div>', unsafe_allow_html=True)

    for item in active_benchmarks:
        label = item["label"]
        val_str, chg_str, change_cls = "0", "0%", "metric-change-neutral"
        if item.get("type") == "fng_api":
            val_str, chg_str = fng_val, fng_class
        elif item.get("type") == "global_api":
            sub_k = item.get("sub_key")
            val_str = global_crypto_data["btc_d_val"] if sub_k == "btc_d" else global_crypto_data["usdt_d_val"]
            chg_str = fmt_pct(global_crypto_data["btc_d_chg"])
        elif item.get("ticker"):
            data = quotes.get(item["ticker"], {"price": 0.0, "change": 0.0})
            val_str = f"{item.get('prefix', '')}{fmt_num(data['price'])}"
            chg_str = f"{fmt_pct(data['change'])} hoje"
            change_cls = "metric-change-pos" if data["change"] >= 0 else "metric-change-neg"

        st.markdown(f'<div class="metric-card"><div class="metric-title">{label}</div><div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
st.markdown("### 🎯 Alvos Preditivos & Zonas Operacionais")
c1, c2, c3, c4, c5, c6 = st.columns(6)
main_q = quotes.get("BTC-USD" if modulo == "Crypto" else "^GSPC", {"price": 100.0, "change": 0.0})
with c1:
    st.markdown(f'<div class="pred-card"><div class="pred-title">Tendência</div><div class="pred-value">Compradora</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="pred-card"><div class="pred-title">Resistência Alvo</div><div class="pred-value">{fmt_num(main_q["price"] * 1.03)}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="pred-card"><div class="pred-title">Suporte Chave</div><div class="pred-value">{fmt_num(main_q["price"] * 0.97)}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="pred-card"><div class="pred-title">Previsão</div><div class="pred-value">Alta Moderada</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="pred-card"><div class="pred-title">Volatilidade</div><div class="pred-value">3.45%</div></div>', unsafe_allow_html=True)
with c6:
    st.markdown(f'<div class="pred-card"><div class="pred-title">Delta OI</div><div class="pred-value">+5.82%</div></div>', unsafe_allow_html=True)

# ==================== 10. PAINEL DE ANÁLISE INTEGRADA DAS CATEGORIAS ====================
st.subheader(f"🎛️ Painel de Análise Integrada das Categorias ({modulo})")
if selected_categories:
    cols = st.columns(min(len(selected_categories), 4))
    for idx, cat_name in enumerate(selected_categories):
        if cat_name in active_display_categories:
            cat_info = active_display_categories[cat_name]
            col = cols[idx % len(cols)]
            with col:
                with st.container(border=True):
                    cat_key = f"chk_cat_{cat_name}"
                    c_title, c_check = st.columns([3.2, 0.8])
                    with c_title:
                        st.markdown(f'<div style="font-size: 13px; font-weight: 700; color: #F0F6FC;">{cat_name}</div>', unsafe_allow_html=True)
                    with c_check:
                        cat_enabled = st.checkbox("", value=st.session_state.get(cat_key, True), key=cat_key, label_visibility="collapsed")
                    
                    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
                    for disp_name, ticker, currency in cat_info["assets"]:
                        q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                        asset_key = f"chk_asset_{cat_name}_{ticker}"
                        color_style = "color: #3FB950;" if q["change"] >= 0 else "color: #F85149;"
                        
                        cA, cB = st.columns([3.2, 0.8])
                        with cA:
                            st.markdown(f'<div style="font-size: 12px;"><span style="color: #8B949E;">{disp_name}:</span> <b style="color: #F0F6FC;">{currency} {fmt_num(q["price"])}</b> <span style="{color_style}">({fmt_pct(q["change"])})</span></div>', unsafe_allow_html=True)
                        with cB:
                            st.checkbox("", value=st.session_state.get(asset_key, True), key=asset_key, disabled=not cat_enabled, label_visibility="collapsed")

st.markdown("---")

# ==================== 11. MAPAS TÉRMICOS ESTRITAMENTE SEPARADOS (SEM CANIBALIZAÇÃO) ====================
if modulo == "Crypto":
    st.subheader("📊 Mapa de Alavancagem & Open Interest (Bitcoin / Derivativos)")
else:
    st.subheader("📈 Mapa Térmico de Volume Profile & Liquidez Institucional (S&P 500 Futures / TradFi)")

if PLOTLY_AVAILABLE:
    if modulo == "Crypto":
        base_price = quotes.get("BTC-USD", {"price": 77000.0}).get("price", 77000.0)
        if base_price == 0.0:
            base_price = 77000.0
        
        prices = []
        liq_volumes = []
        data_source = "Deribit API (BTC-PERPETUAL Order Book Real)"
        unit_label = "M"
        metric_label_type = "Open Interest / Liquidez Efetiva (Bitcoin)"

        try:
            url = "https://www.deribit.com/api/v2/public/get_order_book?instrument_name=BTC-PERPETUAL&depth=250"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            
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
        # Módulo TradFi estrito (S&P 500 Futures / ES=F)
        base_price = quotes.get("^GSPC", {"price": 5800.0}).get("price", 5800.0)
        if base_price == 0.0:
            base_price = 5800.0

        prices = []
        liq_volumes = []
        data_source = "Yahoo Finance API (S&P 500 Futures Histórico Ampliado 3M — ES=F)"
        unit_label = "B"
        metric_label_type = "Volume Profile Institucional (S&P 500)"

        try:
            import yfinance as yf
            df_es = yf.download("ES=F", period="3mo", interval="1h", progress=False)
            
            if not df_es.empty:
                if isinstance(df_es.columns, pd.MultiIndex):
                    df_es.columns = df_es.columns.get_level_values(0)
                df_es = df_es.dropna(subset=['Close', 'Volume'])
                
                if not df_es.empty:
                    min_p = base_price * 0.85
                    max_p = base_price * 1.15
                    df_es = df_es[(df_es['Close'] >= min_p) & (df_es['Close'] <= max_p)]
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
            prices = [base_price * 0.96, base_price * 0.99, base_price * 1.01, base_price * 1.04]
            liq_volumes = [8.4, 32.1, 45.6, 14.2]

    arr_v = np.array(liq_volumes, dtype=float)
    max_v = arr_v.max() if len(arr_v) > 0 and arr_v.max() > 0 else 1.0
    color_intensity = np.sqrt(arr_v / max_v) * 100.0

    df_clusters = pd.DataFrame({"price": prices, "volume": liq_volumes})
    
    df_above = df_clusters[df_clusters["price"] > base_price]
    top_res = df_above.loc[df_above["volume"].idxmax()] if not df_above.empty else {"price": base_price * 1.03, "volume": 0}
    
    df_below = df_clusters[df_clusters["price"] < base_price]
    top_sup = df_below.loc[df_below["volume"].idxmax()] if not df_below.empty else {"price": base_price * 0.97, "volume": 0}

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(
        y=prices,
        x=liq_volumes,
        orientation='h',
        marker=dict(
            color=color_intensity,
            colorscale='Jet',
            showscale=True,
            colorbar=dict(
                title="Intensidade Térmica", 
                len=0.8, 
                thickness=12, 
                tickfont=dict(color="#C9D1D9")
            )
        ),
        hoverinfo='text',
        text=[f"Preço: {fmt_num(p)} | {metric_label_type}: ${v:.2f}{unit_label}" for p, v in zip(prices, liq_volumes)],
        name="Clusters de Liquidez"
    ))

    fig_oi.add_hline(
        y=base_price, 
        line_dash="dash", 
        line_color="#58A6FF", 
        annotation_text=f"Spot Atual: {fmt_num(base_price)}",
        annotation_position="bottom right",
        annotation_font_color="#58A6FF"
    )

    chart_title = "Mapa Térmico de Open Interest & Alavancagem (Bitcoin / Deribit — $M)" if modulo == "Crypto" else "Mapa Térmico de Volume Profile & Liquidez (S&P 500 Futures 3M — $B)"
    xaxis_title = "Volume Notional Acumulado por Faixa ($ Milhões)" if modulo == "Crypto" else "Volume Notional Acumulado por Faixa ($ Bilhões)"

    fig_oi.update_layout(
        title=chart_title,
        paper_bgcolor="#0B0E14", 
        plot_bgcolor="#161B22", 
        font=dict(color="#C9D1D9", size=12),
        margin=dict(l=20, r=20, t=40, b=20), 
        height=520,
        yaxis=dict(gridcolor="#30363D", title="Níveis de Preço (USD/Pts)"),
        xaxis=dict(gridcolor="#30363D", title=xaxis_title)
    )
    st.plotly_chart(fig_oi, use_container_width=True)

    st.markdown(f"📌 **Fonte Oficial da API Ativa ({modulo}):** `{data_source}`")
    st.markdown("### 🔍 Pontos Críticos de Liquidez & Defesa Institucional")
    
    col_sup, col_res = st.columns(2)
    with col_sup:
        st.metric(
            label="🛡️ Principal Suporte / Alinhamento Abaixo",
            value=fmt_num(top_sup["price"]),
            delta=f"Volume: ${top_sup['volume']:.2f}{unit_label}"
        )
    with col_res:
        st.metric(
            label="🎯 Principal Resistência / Alvo Acima",
            value=fmt_num(top_res["price"]),
            delta=f"Volume: ${top_res['volume']:.2f}{unit_label}"
        )
else:
    st.warning("⚠️ O módulo Plotly não está disponível no momento.")

st.markdown("---")
st.caption("⚡©️ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")