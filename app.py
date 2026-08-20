import streamlit as st
import yfinance as yf
import requests
from datetime import datetime
import pandas as pd

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
        padding: 10px 18px;
        border-radius: 8px;
        border: 1px solid #1E293B;
        margin-bottom: 20px;
        color: #94A3B8;
        font-size: 13px;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #21262D;
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
    .category-card {
        background-color: #161B22;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 15px;
        min-height: 180px;
    }
    .category-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #21262D;
        padding-bottom: 8px;
        margin-bottom: 10px;
    }
    .category-title {
        font-size: 13px;
        font-weight: 700;
        color: #58A6FF;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .category-tag {
        font-size: 10px;
        background-color: #21262D;
        color: #8B949E;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .asset-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        font-size: 12px;
    }
    .asset-symbol {
        color: #C9D1D9;
        font-weight: 500;
    }
    .premium-badge { color: #58A6FF; font-weight: bold; }

    [data-testid="stMetricValue"] {
        font-size: 15px !important;
        font-weight: 700 !important;
        white-space: nowrap;
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #8B949E !important;
        white-space: nowrap;
    }
    [data-testid="stMetricDelta"] {
        font-size: 11px !important;
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
    {"key": "SPX", "ticker": "^GSPC", "label": "1. S&P 500 / SPX", "unit": "pts", "prefix": "", "badge": "yfinance API"},
    {"key": "IBOV", "ticker": "^BVSP", "label": "2. Ibovespa / IBOV", "unit": "pts", "prefix": "", "badge": "yfinance API"},
    {"key": "BRENT", "ticker": "BZ=F", "label": "3. Petróleo Brent", "unit": "USD", "prefix": "$ ", "badge": "yfinance API"},
    {"key": "GOLD", "ticker": "GC=F", "label": "4. Ouro Spot", "unit": "USD", "prefix": "$ ", "badge": "yfinance API"},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "5. USD / BRL / Dólar Real", "unit": "pts", "prefix": "R$ ", "badge": "yfinance API"}
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
            ("DOGE Perp", "DOGE-USD", "$"),
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
            ("UNI (Uniswap)", "UNI-USD", "$"),
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
    {"key": "BTC", "ticker": "BTC-USD", "label": "1. Bitcoin / BTC", "prefix": "$ ", "badge": "yfinance API"},
    {"key": "ETH", "ticker": "ETH-USD", "label": "2. Ethereum / ETH", "prefix": "$ ", "badge": "yfinance API"},
    {"key": "BTC_D", "type": "global_api", "sub_key": "btc_d", "label": "3. Bitcoin Dominance / BTC.D", "badge": "CoinGecko API"},
    {"key": "TOTAL_MCAP", "type": "global_api", "sub_key": "total_mcap", "label": "4. Total Crypto Market Cap", "badge": "CoinGecko API"},
    {"key": "FEAR_GREED", "type": "fng_api", "label": "5. Bitcoin Fear & Greed Index", "badge": "Alternative.me API"}
]

# -----------------------------------------------------------------------------
# 3. FUNÇÕES DE FORMATAÇÃO E INGESTÃO DE DADOS (CACHE 10 MIN)
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

@st.cache_data(ttl=600)
def fetch_btc_fng():
    try:
        res = requests.get("https://api.alternative.me/fng/", timeout=5)
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
    """Upgrade 1: Obtém BTC Dominance e Total Market Cap em tempo real."""
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global", timeout=5)
        if res.status_code == 200:
            data = res.json()["data"]
            btc_d = data.get("market_cap_percentage", {}).get("btc", 56.8)
            total_mcap = data.get("total_market_cap", {}).get("usd", 0)
            mcap_trillion = total_mcap / 1e12
            return {
                "btc_d_val": f"{btc_d:.2f}%".replace(".", ","),
                "btc_d_chg": "Ao Vivo",
                "mcap_val": f"$ {mcap_trillion:.2f} T".replace(".", ","),
                "mcap_chg": "Ao Vivo"
            }
    except Exception:
        pass
    return {
        "btc_d_val": "56,80%",
        "btc_d_chg": "Estimado",
        "mcap_val": "$ 2,28 T",
        "mcap_chg": "Estimado"
    }

@st.cache_data(ttl=600)
def fetch_realtime_quotes(symbols_tuple):
    unique_symbols = list(set(symbols_tuple))
    quotes = {}
    if not unique_symbols:
        return quotes

    try:
        data = yf.download(unique_symbols, period="5d", interval="1d", group_by="ticker", progress=False, threads=True)
        for sym in unique_symbols:
            try:
                sub_df = data if len(unique_symbols) == 1 else data[sym]
                sub_df = sub_df.dropna(subset=['Close'])
                if len(sub_df) >= 2:
                    curr = float(sub_df['Close'].iloc[-1])
                    prev = float(sub_df['Close'].iloc[-2])
                    chg = float(((curr - prev) / prev) * 100)
                    quotes[sym] = {"price": curr, "change": chg}
                elif len(sub_df) == 1:
                    quotes[sym] = {"price": float(sub_df['Close'].iloc[-1]), "change": 0.0}
            except Exception:
                pass
    except Exception:
        pass

    for sym in unique_symbols:
        if sym not in quotes or quotes[sym]["price"] == 0.0:
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="5d")
                if not hist.empty:
                    hist = hist.dropna(subset=['Close'])
                    if len(hist) >= 2:
                        curr = float(hist['Close'].iloc[-1])
                        prev = float(hist['Close'].iloc[-2])
                        chg = float(((curr - prev) / prev) * 100)
                        quotes[sym] = {"price": curr, "change": chg}
                    elif len(hist) == 1:
                        quotes[sym] = {"price": float(hist['Close'].iloc[-1]), "change": 0.0}
            except Exception:
                quotes[sym] = {"price": 0.0, "change": 0.0}

    return quotes

# -----------------------------------------------------------------------------
# 4. SIDEBAR: CONTROLE DE TIERS, CATEGORIAS, FORMATOS E PARÂMETROS QUANT
# -----------------------------------------------------------------------------
st.sidebar.title("⚡ Configurações OMNI")
st.sidebar.caption("Controle de geração de roteiros e relatórios")

idioma = st.sidebar.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English", "Español"])
modulo = st.sidebar.radio("💡 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Nível de Acesso (Tier SaaS)")

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
    st.sidebar.info("🔒 Modo Free: 32 ativos fixos padrão. Sem alteração.")
elif "Standard" in tier_selected:
    max_assets_allowed = 32
    max_free_tickers = 5
    allow_customization = True
    allow_white_label = False
    st.sidebar.success("⚡ Modo Standard: Personalizável + 5 Tickers Livres.")
else:
    max_assets_allowed = 100
    max_free_tickers = 999
    allow_customization = True
    allow_white_label = True
    st.sidebar.success("🚀 Modo Premium: 100+ Ativos + White-Label Habilitado.")

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Calibragem (SaaS Enterprise)")
st.sidebar.caption("Selecione os setores/categorias:")

selected_categories = []
for key in active_categories.keys():
    if st.sidebar.checkbox(key, value=True):
        selected_categories.append(key)

# Injeção de Tickers Livres
custom_tickers = []
if allow_customization:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Injeção de Tickers Livres")
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3.SA, PEPE-USD):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()]
        if len(custom_tickers) > max_free_tickers:
            st.sidebar.warning(f"Limite do plano: apenas {max_free_tickers} adicionados.")
            custom_tickers = custom_tickers[:max_free_tickers]

# Upgrade 4: Controles de Parâmetros do Engine Preditivo
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Parâmetros do Engine Preditivo")
horizonte_pred = st.sidebar.selectbox("Horizonte Temporário:", ["24 Horas", "48 Horas", "7 Dias"], index=1)
alvo_pct = st.sidebar.slider("Projeção de Resposta (%)", min_value=0.5, max_value=15.0, value=3.0, step=0.5)
stop_pct = st.sidebar.slider("Zona de Suporte / Defesa (%)", min_value=0.5, max_value=15.0, value=3.0, step=0.5)

st.sidebar.markdown("---")
formato = st.sidebar.radio(f"🎯 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube Auto-Pilot)"], index=0)

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Personalização White-Label")
    company_name = st.sidebar.text_input("Nome da Casa/Escritório:", "XP / BTG / Gestora")
    cnpi_code = st.sidebar.text_input("Registro CNPI/Responsável:", "CNPI-T 3421")

# Compilando Lista Única de Tickers para Download
symbols_to_fetch = []
for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS:
    if item.get("ticker"):
        symbols_to_fetch.append(item["ticker"])

for cat_info in active_categories.values():
    for _, ticker, _ in cat_info["assets"]:
        symbols_to_fetch.append(ticker)

symbols_to_fetch.extend(custom_tickers)

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch))
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()

# Upgrade 2: Montagem de Categoria Exclusiva de Tickers Customizados se existirem
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
# 5. CORPO PRINCIPAL & PAINEL DE CONTROLE
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏛️ {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")

col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(
        f'<div class="status-bar">🕒 <b>Dados consolidados das {now_str}</b> (Cache 10m) | Status API: <span style="color: #3FB950;">● Online</span> | <b>Módulo:</b> {modulo} | <b>Plano:</b> <span class="premium-badge">{tier_selected.split()[0]}</span></div>',
        unsafe_allow_html=True
    )
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

col_left, col_right = st.columns([1.3, 1])

# Painel Esquerdo: Relatório B2B ou Roteiro B2C
with col_left:
    st.subheader(f"📄 Entrega Padrão — {formato}")
    st.caption("Indicadores e cotações integrados em tempo real via API:")

    if "B2B" in formato:
        if modulo == "Crypto":
            btc_q = quotes.get("BTC-USD", {"price": 0.0, "change": 0.0})
            eth_q = quotes.get("ETH-USD", {"price": 0.0, "change": 0.0})

            report_lines = [
                "=== RELATÓRIO INSTITUCIONAL CRYPTO (B2B) ===",
                f"Data/Hora: {now_str}",
                "",
                "1. PANORAMA & BENCHMARKS CRYPTO (MÉTRICAS AGREGADAS)",
                f"- 1. Bitcoin (BTC/USD): $ {fmt_num(btc_q['price'])} ({fmt_pct(btc_q['change'])} hoje) [yfinance API]",
                f"- 2. Ethereum (ETH/USD): $ {fmt_num(eth_q['price'])} ({fmt_pct(eth_q['change'])} hoje) [yfinance API]",
                f"- 3. Bitcoin Dominance (BTC.D): {global_crypto_data['btc_d_val']} ({global_crypto_data['btc_d_chg']}) [CoinGecko API]",
                f"- 4. Total Crypto Market Cap: {global_crypto_data['mcap_val']} ({global_crypto_data['mcap_chg']}) [CoinGecko API]",
                f"- 5. Bitcoin Fear & Greed Index: {fng_val} ({fng_class}) [Alternative.me API]",
                "",
                "2. ANÁLISE INTEGRADA DAS CATEGORIAS CRYPTO SELECIONADAS"
            ]
        else:
            brent_q = quotes.get("BZ=F", {"price": 0.0, "change": 0.0})
            gold_q = quotes.get("GC=F", {"price": 0.0, "change": 0.0})
            spx_q = quotes.get("^GSPC", {"price": 0.0, "change": 0.0})
            ibov_q = quotes.get("^BVSP", {"price": 0.0, "change": 0.0})
            usdbrl_q = quotes.get("BRL=X", {"price": 0.0, "change": 0.0})

            report_lines = [
                "=== RELATÓRIO INSTITUCIONAL TRADFI (MACRO) (B2B) ===",
                f"Data/Hora: {now_str}",
                "",
                "1. PANORAMA & BENCHMARKS DE MERCADO (DADOS VIA YFINANCE API)",
                f"- 1. S&P 500 / SPX: {fmt_num(spx_q['price'])} ({fmt_pct(spx_q['change'])} hoje) [yfinance API]",
                f"- 2. Ibovespa / IBOV: {fmt_num(ibov_q['price'])} ({fmt_pct(ibov_q['change'])} hoje) [yfinance API]",
                f"- 3. Petróleo Brent: $ {fmt_num(brent_q['price'])} ({fmt_pct(brent_q['change'])} hoje) [yfinance API]",
                f"- 4. Ouro Spot: $ {fmt_num(gold_q['price'])} ({fmt_pct(gold_q['change'])} hoje) [yfinance API]",
                f"- 5. USD / BRL / Dólar Real: R$ {fmt_num(usdbrl_q['price'])} ({fmt_pct(usdbrl_q['change'])} hoje) [yfinance API]",
                "",
                "2. ANÁLISE INTEGRADA DAS CATEGORIAS SELECIONADAS (DADOS EM TEMPO REAL)"
            ]

        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_info = active_display_categories[cat_name]
                report_lines.append(f"\n• {cat_name.upper()} ({cat_info['tag']}):")
                for disp_name, ticker, currency in cat_info["assets"]:
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    report_lines.append(f"  - {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")

        if allow_white_label and company_name != "OMNIRESEARCH Engine":
            report_lines.append(f"\nDocumento emitido exclusivamente por {company_name} | Responsável: {cnpi_code}")
        else:
            report_lines.append("\nPowered by OMNIRESEARCH Engine")

        output_content = "\n".join(report_lines)
        st.text_area("", value=output_content, height=350)

        # Upgrade 3: Botão de Download do Relatório B2B
        st.download_button(
            label="📥 Baixar Relatório (TXT)",
            data=output_content,
            file_name=f"OMNI_Relatorio_{modulo}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

    else: # Modo B2C Auto-Pilot (YouTube)
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

        # Upgrade 3: Botão de Download do Roteiro B2C
        st.download_button(
            label="📥 Baixar Roteiro YouTube (TXT)",
            data=script_text,
            file_name=f"OMNI_Roteiro_YouTube_{modulo}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

    # Cards Preditivos Dinâmicos com Parâmetros Calibráveis
    c1, c2, c3, c4 = st.columns(4)
    if modulo == "Crypto":
        main_q = quotes.get("BTC-USD", {"price": 0.0, "change": 0.0})
        res_calc = main_q['price'] * (1 + (alvo_pct / 100))
        sup_calc = main_q['price'] * (1 - (stop_pct / 100))
        target_calc = main_q['price'] * (1 + ((alvo_pct * 0.7) / 100))
        
        with c1:
            st.metric("Tendência (BTC)", "Compradora" if main_q['change'] >= 0 else "Vendedora", f"{fmt_pct(main_q['change'])}")
        with c2:
            st.metric("Resistência Alvo", f"$ {fmt_num(res_calc, dec=0)}", f"+{alvo_pct}%")
        with c3:
            st.metric("Suporte Chave", f"$ {fmt_num(sup_calc, dec=0)}", f"-{stop_pct}%")
        with c4:
            st.metric(f"Previsão {horizonte_pred}", "Alta Moderada", f"Alvo $ {fmt_num(target_calc, dec=0)}")
    else:
        main_q = quotes.get("^GSPC", {"price": 0.0, "change": 0.0})
        res_calc = main_q['price'] * (1 + (alvo_pct / 100))
        sup_calc = main_q['price'] * (1 - (stop_pct / 100))
        target_calc = main_q['price'] * (1 + ((alvo_pct * 0.5) / 100))

        with c1:
            st.metric("Tendência (Macro)", "Compradora" if main_q['change'] >= 0 else "Vendedora", f"{fmt_pct(main_q['change'])}")
        with c2:
            st.metric("Resistência Alvo", f"{fmt_num(res_calc, dec=0)}", f"+{alvo_pct}%")
        with c3:
            st.metric("Suporte Chave", f"{fmt_num(sup_calc, dec=0)}", f"-{stop_pct}%")
        with c4:
            st.metric(f"Previsão {horizonte_pred}", "Alta Moderada", f"Alvo {fmt_num(target_calc, dec=0)}")

# Painel Direito: Métricas Agregadas Estilizadas (Cards HTML)
with col_right:
    st.subheader(f"📊 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado via API / Dados de Mercado às {datetime.now().strftime('%H:%M:%S BRT')}")

    for item in active_benchmarks:
        label = item["label"]
        badge = item.get("badge", "Data Feed")
        
        if item.get("type") == "fng_api":
            val_str = fng_val
            chg_str = fng_class
            change_cls = "metric-change-neutral" if "Greed" in chg_str or "Fear" in chg_str else "metric-change-pos"
        elif item.get("type") == "global_api":
            sub_k = item.get("sub_key")
            if sub_k == "btc_d":
                val_str = global_crypto_data["btc_d_val"]
                chg_str = global_crypto_data["btc_d_chg"]
            else:
                val_str = global_crypto_data["mcap_val"]
                chg_str = global_crypto_data["mcap_chg"]
            change_cls = "metric-change-pos"
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
# 6. PAINEL DE ANÁLISE INTEGRADA DAS CATEGORIAS (GRID CARDS HTML)
# -----------------------------------------------------------------------------
st.subheader(f"📂 Painel de Análise Integrada das Categorias ({modulo})")
st.caption("Visão detalhada dos setores selecionados no painel lateral com cotações automáticas:")

if selected_categories:
    cols = st.columns(min(len(selected_categories), 4))
    for idx, cat_name in enumerate(selected_categories):
        if cat_name in active_display_categories:
            cat_info = active_display_categories[cat_name]
            col = cols[idx % len(cols)]
            
            card_html = f'<div class="category-card"><div class="category-header"><div class="category-title">{cat_name}</div><div class="category-tag">{cat_info["tag"]}</div></div>'
            
            for disp_name, ticker, currency in cat_info["assets"]:
                q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                color_style = "color: #3FB950;" if q["change"] >= 0 else "color: #F85149;"
                card_html += f'<div class="asset-row"><span class="asset-symbol">{disp_name}:</span><span><b>{currency} {fmt_num(q["price"])}</b> <span style="{color_style} font-size: 11px;">({fmt_pct(q["change"])})</span></span></div>'
                
            card_html += '</div>'
            
            with col:
                st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")

# Rodapé Institucional
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.caption(f"© {datetime.now().year} {company_name}. Todos os direitos reservados. Relatório de uso exclusivo.")
else:
    st.caption("⚡ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")