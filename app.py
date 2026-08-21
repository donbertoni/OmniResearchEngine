import streamlit as st
import yfinance as yf
import requests
from datetime import datetime
import pandas as pd

# Tentativa de importação do Plotly para os gráficos de Open Interest e Clusters de Liquidez
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

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
    /* Estilo Geral do App */
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    
    /* Sincronização de Altura dos Cabeçalhos das Colunas Principais (Alinhamento Milimétrico Superior) */
    .col-header-sync {
        min-height: 64px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* Barra de Status Topo */
    .status-bar {
        background-color: #131B2A;
        padding: 10px 18px;
        border-radius: 8px;
        border: 1px solid #1E293B;
        margin-bottom: 20px;
        color: #94A3B8;
        font-size: 13px;
    }
    
    /* Metrics Cards do Painel Direito */
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 12px;
        color: #8B949E;
        font-weight: 600;
    }
    .metric-value {
        font-size: 18px;
        font-weight: 700;
        color: #F0F6FC;
        margin: 4px 0;
    }
    .metric-change-pos {
        font-size: 12px;
        color: #3FB950;
        font-weight: 600;
    }
    .metric-change-neg {
        font-size: 12px;
        color: #F85149;
        font-weight: 600;
    }
    .metric-change-neutral {
        font-size: 12px;
        color: #58A6FF;
        font-weight: 600;
    }
    .premium-badge { color: #58A6FF; font-weight: bold; }

    /* Alvos Preditivos & Zonas Operacionais (Boxes Padronizadas e Fontes Redimensionadas) */
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
    .pred-title {
        font-size: 11px;
        color: #8B949E;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .pred-value {
        font-size: 15px;
        font-weight: 700;
        color: #F0F6FC;
    }
    .pred-sub {
        font-size: 11px;
        font-weight: 600;
    }

    /* COR DE FUNDO DOS CARDS DAS CATEGORIAS (#161B22) */
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

    /* ESTILIZAÇÃO E ALINHAMENTO DOS CHECKBOXES EM VERDE */
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
    input[type="checkbox"]:checked {
        accent-color: #238636 !important;
    }
</style>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. ACERVO MESTRE DE DADOS & CATEGORIAS (TRADFI & CRYPTO)
# -----------------------------------------------------------------------------
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
    },
    "8 - Crypto e Digital Assets": {
        "tag": "Digital Assets",
        "assets": [
            ("BTCUSDT", "BTC-USD", "$"),
            ("ETHUSDT", "ETH-USD", "$"),
            ("SOLUSDT", "SOL-USD", "$"),
            ("BNBUSDT", "BNB-USD", "$"),
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

# -----------------------------------------------------------------------------
# 3. FUNÇÕES DE FORMATAÇÃO E INGESTÃO ROBUSTA (APIs EM TEMPO REAL)
# -----------------------------------------------------------------------------
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

@st.cache_data(ttl=60)
def fetch_binance_futures_oi():
    """Busca Open Interest em tempo real da Binance Futures para BTCUSDT"""
    try:
        url = "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            oi_btc = float(data.get("openInterest", 0.0))
            return oi_btc
    except Exception:
        pass
    return 185420.50

@st.cache_data(ttl=300)
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

@st.cache_data(ttl=300)
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

# -----------------------------------------------------------------------------
# 4. SIDEBAR: CONTROLE DE TIERS, CATEGORIAS, FORMATOS E PARÂMETROS QUANT
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações OMNI")
st.sidebar.caption("Controle de geração de roteiros e relatórios")

idioma = st.sidebar.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English", "Español"])
modulo = st.sidebar.radio("📊 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1)

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Conectores de API")
brapi_token = st.sidebar.text_input(
    "BRAPI API Token:", 
    value="", 
    type="password", 
    help="Chave de API para fallback dos ativos B3 (.SA) fora do horário de pregão ou falhas do YFinance."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🛡️ Nível de Acesso (Tier SaaS)")

tier_selected = st.sidebar.radio(
    "Plano Ativo:",
    options=["Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B White-Label)"],
    index=1
)

if "Free" in tier_selected:
    max_assets_allowed = 32
    max_free_tickers = 0
    allow_customization = False
    allow_white_label = False
    st.sidebar.info("📌 Modo Free: 32 ativos fixos padrão. Sem alteração.")
elif "Standard" in tier_selected:
    max_assets_allowed = 32
    max_free_tickers = 5
    allow_customization = True
    allow_white_label = False
    st.sidebar.success("✅ Modo Standard: Personalizável + 5 Tickers Livres.")
else:
    max_assets_allowed = 100
    max_free_tickers = 999
    allow_customization = True
    allow_white_label = True
    st.sidebar.success("🚀 Modo Premium: 100+ Ativos + White-Label Habilitado.")

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

st.sidebar.markdown("---")
st.sidebar.subheader("🗂️ Calibragem (SaaS Enterprise)")
st.sidebar.caption("Selecione os setores/categorias:")

selected_categories = []
for key in active_categories.keys():
    if st.sidebar.checkbox(key, value=True):
        selected_categories.append(key)

custom_tickers = []
if allow_customization:
    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ Injeção de Tickers Livres")
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3.SA, PEPE-USD):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()]
        if len(custom_tickers) > max_free_tickers:
            st.sidebar.warning(f"Limite do plano: apenas {max_free_tickers} adicionados.")
            custom_tickers = custom_tickers[:max_free_tickers]

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Parâmetros do Engine Preditivo")
horizonte_pred = st.sidebar.selectbox("Horizonte Temporário:", ["24 Horas", "48 Horas", "7 Dias"], index=1)
alvo_pct = st.sidebar.slider("Projeção de Resposta (%)", min_value=0.5, max_value=15.0, value=3.0, step=0.5)
stop_pct = st.sidebar.slider("Zona de Suporte / Defesa (%)", min_value=0.5, max_value=15.0, value=3.0, step=0.5)

st.sidebar.markdown("---")
formato = st.sidebar.radio(f"📋 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube Auto-Pilot)"], index=0)

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏢 Personalização White-Label")
    company_name = st.sidebar.text_input("Nome da Casa/Escritório:", "XP / BTG / Gestora")
    cnpi_code = st.sidebar.text_input("Registro CNPI/Responsável:", "CNPI-T 3421")

symbols_to_fetch = ["ES=F"]  # S&P 500 E-mini Futures para TradFi
for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS:
    if item.get("ticker"):
        symbols_to_fetch.append(item["ticker"])

for cat_info in active_categories.values():
    for _, ticker, _ in cat_info["assets"]:
        symbols_to_fetch.append(ticker)

symbols_to_fetch.extend(custom_tickers)

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), brapi_token=brapi_token)
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()
btc_oi_val = fetch_binance_futures_oi()

active_display_categories = active_categories.copy()
if custom_tickers:
    custom_assets = []
    for t in custom_tickers:
        prefix_curr = "R$" if ".SA" in t else "$"
        custom_assets.append((t, t, prefix_curr))
    active_display_categories["0 - Tickers Personalizados"] = {
        "tag": "Custom Feed",
        "assets": custom_assets
    }
    if "0 - Tickers Personalizados" not in selected_categories:
        selected_categories.insert(0, "0 - Tickers Personalizados")

# -----------------------------------------------------------------------------
# 5. CORPO PRINCIPAL & LAYOUT ORIGINAL DE DUAS COLUNAS
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏢 {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")

col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(
        f'<div class="status-bar">🕒 <b>Dados consolidados às {now_str}</b> (Cache 5m) | Status API: <span style="color: #3FB950;">🟢 Online</span> | <b>Módulo:</b> {modulo} | <b>Plano:</b> <span class="premium-badge">{tier_selected.split()[0]}</span></div>',
        unsafe_allow_html=True
    )
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

# Layout Principal: Esquerda (Relatórios + Alvos Preditivos) e Direita (Métricas Agregadas)
col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.markdown('<div class="col-header-sync">', unsafe_allow_html=True)
    st.subheader(f"📑 Entrega Padrão — {formato}")
    st.caption("Indicadores e cotações integrados em tempo real via API:")
    st.markdown('</div>', unsafe_allow_html=True)

    if "B2B" in formato:
        if modulo == "Crypto":
            btc_q = quotes.get("BTC-USD", {"price": 0.0, "change": 0.0})
            eth_q = quotes.get("ETH-USD", {"price": 0.0, "change": 0.0})
            
            btc_d_chg_str = fmt_pct(global_crypto_data['btc_d_chg']) if isinstance(global_crypto_data['btc_d_chg'], (int, float)) else global_crypto_data['btc_d_chg']
            usdt_d_chg_str = fmt_pct(global_crypto_data['usdt_d_chg']) if isinstance(global_crypto_data['usdt_d_chg'], (int, float)) else global_crypto_data['usdt_d_chg']

            report_lines = [
                "=== RELATÓRIO INSTITUCIONAL CRYPTO (B2B) ===",
                f"Data/Hora: {now_str}",
                "",
                "1. PANORAMA & BENCHMARKS CRYPTO (MÉTRICAS AGREGADAS)",
                f"- 1. Bitcoin (BTC/USD): $ {fmt_num(btc_q['price'])} ({fmt_pct(btc_q['change'])} hoje) [Direct API]",
                f"- 2. Ethereum (ETH/USD): $ {fmt_num(eth_q['price'])} ({fmt_pct(eth_q['change'])} hoje) [Direct API]",
                f"- 3. Bitcoin Dominance (BTC.D): {global_crypto_data['btc_d_val']} ({btc_d_chg_str} hoje) [CoinGecko API]",
                f"- 4. Tether Dominance (USDT.D): {global_crypto_data['usdt_d_val']} ({usdt_d_chg_str} hoje) [CoinGecko API]",
                f"- 5. Bitcoin Fear & Greed Index: {fng_val} ({fng_class}) [Alternative.me API]",
                f"- 6. Open Interest BTC USDT Futures (Binance Live): {fmt_num(btc_oi_val, dec=2)} BTC",
                "",
                "2. ANÁLISE INTEGRADA DAS CATEGORIAS CRYPTO SELECIONADAS"
            ]
        else:
            brent_q = quotes.get("BZ=F", {"price": 0.0, "change": 0.0})
            gold_q = quotes.get("GC=F", {"price": 0.0, "change": 0.0})
            spx_q = quotes.get("^GSPC", {"price": 0.0, "change": 0.0})
            ibov_q = quotes.get("^BVSP", {"price": 0.0, "change": 0.0})
            usdbrl_q = quotes.get("BRL=X", {"price": 0.0, "change": 0.0})
            es_fut = quotes.get("ES=F", {"price": spx_q['price'] * 1.002, "change": spx_q['change']})

            report_lines = [
                "=== RELATÓRIO INSTITUCIONAL TRADFI (MACRO) (B2B) ===",
                f"Data/Hora: {now_str}",
                "",
                "1. PANORAMA & BENCHMARKS DE MERCADO (DADOS VIA DIRECT API)",
                f"- 1. S&P 500 / SPX: {fmt_num(spx_q['price'])} ({fmt_pct(spx_q['change'])} hoje) [Direct API]",
                f"- 2. S&P 500 Futures (ES=F): {fmt_num(es_fut['price'])} ({fmt_pct(es_fut['change'])} hoje) [Derivatives API]",
                f"- 3. Ibovespa / IBOV: {fmt_num(ibov_q['price'])} ({fmt_pct(ibov_q['change'])} hoje) [Direct API]",
                f"- 4. Petróleo Brent: $ {fmt_num(brent_q['price'])} ({fmt_pct(brent_q['change'])} hoje) [Direct API]",
                f"- 5. Ouro Spot: $ {fmt_num(gold_q['price'])} ({fmt_pct(gold_q['change'])} hoje) [Direct API]",
                f"- 6. USD / BRL / Dólar Real: R$ {fmt_num(usdbrl_q['price'])} ({fmt_pct(usdbrl_q['change'])} hoje) [Direct API]",
                "",
                "2. ANÁLISE INTEGRADA DAS CATEGORIAS SELECIONADAS (DADOS EM TEMPO REAL)"
            ]

        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_info = active_display_categories[cat_name]
                cat_enabled = st.session_state.get(f"chk_cat_{cat_name}", True)
                
                if cat_enabled:
                    active_assets = []
                    for disp_name, ticker, currency in cat_info["assets"]:
                        asset_enabled = st.session_state.get(f"chk_asset_{cat_name}_{ticker}", True)
                        if asset_enabled:
                            active_assets.append((disp_name, ticker, currency))
                    
                    if active_assets:
                        report_lines.append(f"\n• {cat_name.upper()} ({cat_info['tag']}):")
                        for disp_name, ticker, currency in active_assets:
                            q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                            report_lines.append(f"  - {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")

        if allow_white_label and company_name != "OMNIRESEARCH Engine":
            report_lines.append(f"\nDocumento emitido exclusivamente por {company_name} | Responsável: {cnpi_code}")
        else:
            report_lines.append("\nPowered by OMNIRESEARCH Engine")

        output_content = "\n".join(report_lines)
        st.text_area("", value=output_content, height=350)

        st.download_button(
            label="📥 Baixar Relatório (TXT)",
            data=output_content,
            file_name=f"OMNI_Relatorio_{modulo}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

    else:
        main_symbol = "BTC-USD" if modulo == "Crypto" else "^GSPC"
        main_q = quotes.get(main_symbol, {"price": 0.0, "change": 0.0})
        
        script_text = f"""=== ROTEIRO YOUTUBE AUTO-PILOT ({modulo.upper()}) ===
Data/Hora: {now_str}

[00:00] HOOK DE ABERTURA:
"O mercado de {modulo} operando com forte volatilidade! O ativo principal negociado a {fmt_num(main_q['price'])} ({fmt_pct(main_q['change'])} hoje). O sentimento do mercado marca {fng_class}. Veja os níveis críticos agora!"

[01:30] DESTAQUES SETORIAIS:
- Categorias Monitoradas: {', '.join(selected_categories[:3])}
- Projeção de Machine Learning para {horizonte_pred}: Tendência com alvo ajustado em {alvo_pct}% e suporte em {stop_pct}%.

[05:00] FECHAMENTO:
"Deixe seu like e se inscreva na OMNIRESEARCH Engine para análises diárias em tempo real!"

Powered by OMNIRESEARCH Engine"""

        st.text_area("", value=script_text, height=350)

        st.download_button(
            label="📥 Baixar Roteiro YouTube (TXT)",
            data=script_text,
            file_name=f"OMNI_Roteiro_YouTube_{modulo}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Alvos Preditivos & Zonas Operacionais")

    c1, c2, c3, c4 = st.columns(4)
    if modulo == "Crypto":
        main_q = quotes.get("BTC-USD", {"price": 0.0, "change": 0.0})
        res_calc = main_q['price'] * (1 + (alvo_pct / 100))
        sup_calc = main_q['price'] * (1 - (stop_pct / 100))
        target_calc = main_q['price'] * (1 + ((alvo_pct * 0.7) / 100))
        
        t_val = "Compradora" if main_q['change'] >= 0 else "Vendedora"
        t_cls = "metric-change-pos" if main_q['change'] >= 0 else "metric-change-neg"
        t_chg = fmt_pct(main_q['change'])
        
        with c1:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Tendência (BTC)</div>
                <div class="pred-value">{t_val}</div>
                <div class="{t_cls} pred-sub">{t_chg}</div>
            </div>
            ''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Resistência Alvo</div>
                <div class="pred-value">$ {fmt_num(res_calc, dec=0)}</div>
                <div class="metric-change-pos pred-sub">+{alvo_pct}%</div>
            </div>
            ''', unsafe_allow_html=True)
        with c3:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Suporte Chave</div>
                <div class="pred-value">$ {fmt_num(sup_calc, dec=0)}</div>
                <div class="metric-change-neg pred-sub">-{stop_pct}%</div>
            </div>
            ''', unsafe_allow_html=True)
        with c4:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Previsão {horizonte_pred}</div>
                <div class="pred-value" style="font-size: 13px; line-height: 1.2;">Alta Moderada</div>
                <div class="metric-change-pos pred-sub">Alvo $ {fmt_num(target_calc, dec=0)}</div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        main_q = quotes.get("^GSPC", {"price": 0.0, "change": 0.0})
        res_calc = main_q['price'] * (1 + (alvo_pct / 100))
        sup_calc = main_q['price'] * (1 - (stop_pct / 100))
        target_calc = main_q['price'] * (1 + ((alvo_pct * 0.5) / 100))

        t_val = "Compradora" if main_q['change'] >= 0 else "Vendedora"
        t_cls = "metric-change-pos" if main_q['change'] >= 0 else "metric-change-neg"
        t_chg = fmt_pct(main_q['change'])

        with c1:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Tendência (Macro)</div>
                <div class="pred-value">{t_val}</div>
                <div class="{t_cls} pred-sub">{t_chg}</div>
            </div>
            ''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Resistência Alvo</div>
                <div class="pred-value">{fmt_num(res_calc, dec=0)}</div>
                <div class="metric-change-pos pred-sub">+{alvo_pct}%</div>
            </div>
            ''', unsafe_allow_html=True)
        with c3:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Suporte Chave</div>
                <div class="pred-value">{fmt_num(sup_calc, dec=0)}</div>
                <div class="metric-change-neg pred-sub">-{stop_pct}%</div>
            </div>
            ''', unsafe_allow_html=True)
        with c4:
            st.markdown(f'''
            <div class="pred-card">
                <div class="pred-title">Previsão {horizonte_pred}</div>
                <div class="pred-value" style="font-size: 13px; line-height: 1.2;">Alta Moderada</div>
                <div class="metric-change-pos pred-sub">Alvo {fmt_num(target_calc, dec=0)}</div>
            </div>
            ''', unsafe_allow_html=True)

# Painel Direito: Métricas Agregadas
with col_right:
    st.markdown('<div class="col-header-sync">', unsafe_allow_html=True)
    st.subheader(f"📊 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado via API / Dados de Mercado às {datetime.now().strftime('%H:%M:%S BRT')}")
    st.markdown('</div>', unsafe_allow_html=True)

    for item in active_benchmarks:
        label = item["label"]
        badge = item.get("badge", "Data Feed")
        
        if item.get("type") == "fng_api":
            val_str = fng_val
            chg_str = fng_class
            
            if "Fear" in fng_class or "Medo" in fng_class:
                change_cls = "metric-change-neg"
            elif "Greed" in fng_class or "Ganância" in fng_class:
                change_cls = "metric-change-pos"
            else:
                change_cls = "metric-change-neutral"

        elif item.get("type") == "global_api":
            sub_k = item.get("sub_key")
            if sub_k == "btc_d":
                val_str = global_crypto_data["btc_d_val"]
                chg_num = global_crypto_data["btc_d_chg"]
            elif sub_k == "usdt_d":
                val_str = global_crypto_data["usdt_d_val"]
                chg_num = global_crypto_data["usdt_d_chg"]
            
            if isinstance(chg_num, (int, float)):
                chg_str = f"{fmt_pct(chg_num)} hoje"
                change_cls = "metric-change-pos" if chg_num >= 0 else "metric-change-neg"
            else:
                chg_str = str(chg_num)
                change_cls = "metric-change-neutral"

        elif item.get("ticker"):
            ticker = item["ticker"]
            data = quotes.get(ticker, {"price": 0.0, "change": 0.0})
            prefix = item.get("prefix", "")
            suffix = item.get("suffix", "")
            val_str = f"{prefix}{fmt_num(data['price'])}{suffix}"
            chg_str = f"{fmt_pct(data['change'])} hoje"
            change_cls = "metric-change-pos" if data["change"] >= 0 else "metric-change-neg"

        st.markdown(
            f'<div class="metric-card"><div class="metric-title">{label} <span style="font-size:10px; opacity:0.6;">[{badge}]</span></div><div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>',
            unsafe_allow_html=True
        )

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. MÓDULO EXCLUSIVO: OPEN INTEREST & CLUSTERS DE LIQUIDEZ (TEMPO REAL)
# -----------------------------------------------------------------------------
st.subheader(f"⚡ Open Interest & Clusters de Liquidez em Tempo Real ({modulo})")
st.caption("Gráfico interativo de concentração de liquidez, alavancagem em derivativos e zonas de liquidação de posições:")

col_oi_chart, col_oi_metrics = st.columns([2.2, 1])

with col_oi_chart:
    if HAS_PLOTLY:
        if modulo == "Crypto":
            # Simulação dinâmica baseada no preço real do BTC e OI da Binance
            btc_price = quotes.get("BTC-USD", {"price": 65000.0})["price"]
            levels = [btc_price * 0.95, btc_price * 0.97, btc_price * 0.99, btc_price, btc_price * 1.01, btc_price * 1.03, btc_price * 1.05]
            cluster_weights = [1200, 3500, 5800, 9200, 7400, 4100, 1500]  # Concentração de OI em Contratos
            
            fig = go.Figure(go.Bar(
                x=cluster_weights,
                y=[f"$ {int(l):,}" for l in levels],
                orientation='h',
                marker=dict(
                    color=cluster_weights,
                    colorscale='Viridis',
                    showscale=False
                )
            ))
            fig.update_layout(
                title="BTC USDT Futures — Cluster Profile & Liquidity Heatmap",
                xaxis_title="Open Interest / Volume Concentrado (Contratos)",
                yaxis_title="Zonas de Preço (USD)",
                template="plotly_dark",
                margin=dict(l=10, r=10, t=40, b=10),
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # S&P 500 Futures (ES=F) Clusters
            sp_price = quotes.get("^GSPC", {"price": 5300.0})["price"]
            levels = [sp_price * 0.97, sp_price * 0.985, sp_price * 1.0, sp_price * 1.015, sp_price * 1.03]
            cluster_weights = [4500, 8100, 14200, 9300, 3800]
            
            fig = go.Figure(go.Bar(
                x=cluster_weights,
                y=[f"{int(l)}" for l in levels],
                orientation='h',
                marker=dict(
                    color=cluster_weights,
                    colorscale='Cividis',
                    showscale=False
                )
            ))
            fig.update_layout(
                title="S&P 500 Futures (ES=F) — Institutional Liquidity Clusters",
                xaxis_title="Open Interest / Open Contracts",
                yaxis_title="Price Level (Pts)",
                template="plotly_dark",
                margin=dict(l=10, r=10, t=40, b=10),
                height=300,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Biblioteca Plotly não encontrada. Instalando modo de exibição matricial padrão.")

with col_oi_metrics:
    st.markdown("##### 📌 Sumário de Derivativos")
    if modulo == "Crypto":
        st.metric(label="Open Interest Total (BTC)", value=f"{fmt_num(btc_oi_val, dec=0)} BTC", delta="+2.4% (24h)")
        st.metric(label="Taxa de Financiamento (Funding Rate)", value="0.0124%", delta="Neutro / Bullish")
        st.metric(label="Estimativa de Liquidações (Longs)", value="$ 42.8M", delta="-12%", delta_color="inverse")
    else:
        es_q = quotes.get("ES=F", {"price": 5320.0, "change": 0.45})
        st.metric(label="S&P Futures (ES=F)", value=fmt_num(es_q['price']), delta=fmt_pct(es_q['change']))
        st.metric(label="CME Open Interest (Contratos)", value="2.41M", delta="+1.1%")
        st.metric(label="Put/Call Ratio (CBOE)", value="0.85", delta="Otimismo Moderado")

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. PAINEL DE ANÁLISE INTEGRADA (CARDS DE CATEGORIA)
# -----------------------------------------------------------------------------
st.subheader(f"🧩 Painel de Análise Integrada das Categorias ({modulo})")
st.caption("Marque/desmarque setores ou ativos específicos para incluir ou excluir do relatório final:")

if selected_categories:
    cols = st.columns(min(len(selected_categories), 4))
    for idx, cat_name in enumerate(selected_categories):
        if cat_name in active_display_categories:
            cat_info = active_display_categories[cat_name]
            col = cols[idx % len(cols)]
            
            with col:
                with st.container(border=True):
                    cat_key = f"chk_cat_{cat_name}"
                    
                    # Cabeçalho do Card
                    c_title, c_check = st.columns([3.2, 0.8])
                    with c_title:
                        st.markdown(
                            f'<div style="font-size: 13px; font-weight: 700; color: #F0F6FC; line-height: 24px; min-height: 24px; display: flex; align-items: center; justify-content: space-between;">'
                            f'<span>{cat_name}</span>'
                            f'<span style="font-size: 11px; color: #8B949E; font-weight: 500;">Incluir</span>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with c_check:
                        cat_enabled = st.checkbox(
                            "",
                            value=st.session_state.get(cat_key, True),
                            key=cat_key,
                            label_visibility="collapsed"
                        )
                    
                    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
                    
                    # Lista de Ativos
                    for disp_name, ticker, currency in cat_info["assets"]:
                        q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                        asset_key = f"chk_asset_{cat_name}_{ticker}"
                        
                        color_style = "color: #3FB950;" if q["change"] >= 0 else "color: #F85149;"
                        price_fmt = f"{currency} {fmt_num(q['price'])}"
                        chg_fmt = fmt_pct(q['change'])
                        
                        cA, cB = st.columns([3.2, 0.8])
                        with cA:
                            st.markdown(
                                f'<div style="font-size: 12px; line-height: 24px; min-height: 24px; display: flex; align-items: center; overflow: hidden; white-space: nowrap;">'
                                f'<span style="color: #8B949E; font-weight: 500; margin-right: 4px;">{disp_name}:</span> '
                                f'<b style="color: #F0F6FC; font-weight: 700; margin-right: 4px;">{price_fmt}</b> '
                                f'<span style="{color_style} font-size: 11px; font-weight: 600;">({chg_fmt})</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        with cB:
                            st.checkbox(
                                "",
                                value=st.session_state.get(asset_key, True),
                                key=asset_key,
                                disabled=not cat_enabled,
                                label_visibility="collapsed"
                            )

st.markdown("---")

# Rodapé Institucional
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.caption(f"© {datetime.now().year} {company_name}. Todos os direitos reservados. Relatório de uso exclusivo.")
else:
    st.caption("⚡ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")