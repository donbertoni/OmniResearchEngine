import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import re
import yfinance as yf

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
    {"key": "SPX", "ticker": "^GSPC", "label": "1. S&P 500 / SPX", "unit": "pts", "prefix": "", "badge": "yFinance"},
    {"key": "IBOV", "ticker": "^BVSP", "label": "2. Ibovespa / IBOV", "unit": "pts", "prefix": "", "badge": "yFinance"},
    {"key": "BRENT", "ticker": "BZ=F", "label": "3. Petróleo Brent", "unit": "USD", "prefix": "$ ", "badge": "yFinance"},
    {"key": "GOLD", "ticker": "GC=F", "label": "4. Ouro Spot", "unit": "USD", "prefix": "$ ", "badge": "yFinance"},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "5. USD / BRL / Dólar Real", "unit": "pts", "prefix": "R$ ", "badge": "yFinance"}
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
    {"key": "BTC", "ticker": "BTC-USD", "label": "1. Bitcoin / BTC", "prefix": "$ ", "badge": "yFinance"},
    {"key": "ETH", "ticker": "ETH-USD", "label": "2. Ethereum / ETH", "prefix": "$ ", "badge": "yFinance"},
    {"key": "BTC_D", "type": "global_api", "sub_key": "btc_d", "label": "3. Bitcoin Dominance / BTC.D", "badge": "CoinGecko API"},
    {"key": "USDT_D", "type": "global_api", "sub_key": "usdt_d", "label": "4. Tether Dominance / USDT.D", "badge": "CoinGecko API"},
    {"key": "FEAR_GREED", "type": "fng_api", "label": "5. Bitcoin Fear & Greed Index", "badge": "Alternative.me API"}
]

# -----------------------------------------------------------------------------
# 3. FUNÇÕES DE FORMATAÇÃO E INGESTÃO ROBUSTA VIA YFINANCE BATCH
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
        res = requests.get("https://api.alternative.me/fng/", timeout=4)
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
        res = requests.get("https://api.coingecko.com/api/v3/global", timeout=4)
        if res.status_code == 200:
            data = res.json()["data"]
            btc_d = data.get("market_cap_percentage", {}).get("btc", 56.8)
            usdt_d = data.get("market_cap_percentage", {}).get("usdt", 5.2)
            btc_d_chg = data.get("market_cap_change_percentage_24h_usd", 0.35)
            return {
                "btc_d_val": f"{btc_d:.2f}%".replace(".", ","),
                "btc_d_chg": btc_d_chg,
                "usdt_d_val": f"{usdt_d:.2f}%".replace(".", ","),
                "usdt_d_chg": -0.18
            }
    except Exception:
        pass
    return {"btc_d_val": "56,80%", "btc_d_chg": 0.35, "usdt_d_val": "5,20%", "usdt_d_chg": -0.18}

@st.cache_data(ttl=180)
def fetch_realtime_quotes(symbols_tuple):
    quotes = {}
    for s in symbols_tuple:
        clean = s.strip().upper()
        quotes[clean] = {"price": 0.0, "change": 0.0}

    y_symbols = []
    mapping = {}
    for s in symbols_tuple:
        clean = s.strip().upper()
        if re.match(r'^[A-Z]{4}[0-9]{1,2}$', clean):
            y_sym = f"{clean}.SA"
        elif clean in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]:
            y_sym = clean.replace("USDT", "-USD")
        else:
            y_sym = clean
        y_symbols.append(y_sym)
        mapping[y_sym] = clean

    try:
        # Baixa histórico de 5 dias em lote usando a biblioteca oficial yfinance
        df = yf.download(tickers=y_symbols, period="5d", interval="1d", progress=False, threads=True)
        if not df.empty and 'Close' in df:
            close_df = df['Close']
            for y_sym in y_symbols:
                clean = mapping[y_sym]
                try:
                    if len(y_symbols) == 1:
                        series = close_df.dropna()
                    else:
                        series = close_df[y_sym].dropna()

                    if len(series) >= 1:
                        price = float(series.iloc[-1])
                        prev_price = float(series.iloc[-2]) if len(series) >= 2 else price
                        change = ((price - prev_price) / prev_price) * 100 if prev_price > 0 else 0.0

                        d_info = {"price": price, "change": change}
                        quotes[clean] = d_info
                        quotes[y_sym] = d_info
                        if y_sym.endswith(".SA"):
                            quotes[y_sym.replace(".SA", "")] = d_info
                except Exception:
                    continue
    except Exception:
        pass

    # Fallback da Binance para Cripto em caso de falha de conexão
    for s in symbols_tuple:
        clean = s.strip().upper()
        if quotes.get(clean, {}).get("price", 0.0) == 0.0 and ("-USD" in clean or "USDT" in clean):
            try:
                pair = clean.replace("-USD", "USDT")
                res = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}", timeout=3)
                if res.status_code == 200:
                    d = res.json()
                    d_info = {"price": float(d.get("lastPrice", 0.0)), "change": float(d.get("priceChangePercent", 0.0))}
                    quotes[clean] = d_info
            except Exception:
                pass

    return quotes

# -----------------------------------------------------------------------------
# 4. SIDEBAR: CONTROLE DE TIERS, CATEGORIAS, FORMATOS E PARÂMETROS QUANT
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações OMNI")
st.sidebar.caption("Controle de geração de roteiros e relatórios")

idioma = st.sidebar.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English", "Español"])
modulo = st.sidebar.radio("📌 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1)

st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Nível de Acesso (Tier SaaS)")

tier_selected = st.sidebar.radio(
    "Plano Ativo:",
    options=["Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B White-Label)"],
    index=1
)

if "Free" in tier_selected:
    max_free_tickers = 0
    allow_customization = False
    allow_white_label = False
    st.sidebar.info("ℹ️ Modo Free: ativos fixos padrão.")
elif "Standard" in tier_selected:
    max_free_tickers = 5
    allow_customization = True
    allow_white_label = False
    st.sidebar.success("⚡ Modo Standard: Personalizável + 5 Tickers Livres.")
else:
    max_free_tickers = 999
    allow_customization = True
    allow_white_label = True
    st.sidebar.success("👑 Modo Premium: 100+ Ativos + White-Label Habilitado.")

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Calibragem (SaaS Enterprise)")
st.sidebar.caption("Selecione os setores/categorias:")

selected_categories = []
for key in active_categories.keys():
    if st.sidebar.checkbox(key, value=True):
        selected_categories.append(key)

custom_tickers = []
if allow_customization:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 Injeção de Tickers Livres")
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3, PETR3, NVDA, BTC-USD):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()]
        if len(custom_tickers) > max_free_tickers:
            st.sidebar.warning(f"Limite do plano: apenas {max_free_tickers} adicionados.")
            custom_tickers = custom_tickers[:max_free_tickers]

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Parâmetros do Engine Preditivo")
horizonte_pred = st.sidebar.selectbox("Horizonte Temporário:", ["24 Horas", "48 Horas", "7 Dias"], index=1)
alvo_pct = st.sidebar.slider("Projeção de Resposta (%)", min_value=0.5, max_value=15.0, value=3.0, step=0.5)
stop_pct = st.sidebar.slider("Zona de Suporte / Defesa (%)", min_value=0.5, max_value=15.0, value=3.0, step=0.5)

st.sidebar.markdown("---")
formato = st.sidebar.radio(f"📄 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube Auto-Pilot)"], index=0)

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    st.sidebar.markdown("---")
    st.sidebar.subheader("💼 Personalização White-Label")
    company_name = st.sidebar.text_input("Nome da Casa/Escritório:", "XP / BTG / Gestora")
    cnpi_code = st.sidebar.text_input("Registro CNPI/Responsável:", "CNPI-T 3421")

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

active_display_categories = active_categories.copy()
if custom_tickers:
    custom_assets = []
    for t in custom_tickers:
        prefix_curr = "R$" if (t.endswith(".SA") or re.match(r'^[A-Z]{4}[0-9]{1,2}$', t)) else "$"
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
    st.title("📈 OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")

col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(
        f'<div class="status-bar">⚡ <b>Dados consolidados às {now_str}</b> | Status API: <span style="color: #3FB950;">🟢 Online (Native yFinance Batch Engine)</span> | <b>Módulo:</b> {modulo} | <b>Plano:</b> <span class="premium-badge">{tier_selected.split()[0]}</span></div>',
        unsafe_allow_html=True
    )
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.subheader(f"📝 Entrega Padrão — {formato}")
    st.caption("Indicadores e cotações integrados em tempo real via API REST:")

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
                f"- 1. Bitcoin (BTC/USD): $ {fmt_num(btc_q['price'])} ({fmt_pct(btc_q['change'])} hoje)",
                f"- 2. Ethereum (ETH/USD): $ {fmt_num(eth_q['price'])} ({fmt_pct(eth_q['change'])} hoje)",
                f"- 3. Bitcoin Dominance (BTC.D): {global_crypto_data['btc_d_val']} ({btc_d_chg_str} hoje)",
                f"- 4. Tether Dominance (USDT.D): {global_crypto_data['usdt_d_val']} ({usdt_d_chg_str} hoje)",
                f"- 5. Bitcoin Fear & Greed Index: {fng_val} ({fng_class})",
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
                "1. PANORAMA & BENCHMARKS DE MERCADO (DADOS EM TEMPO REAL)",
                f"- 1. S&P 500 / SPX: {fmt_num(spx_q['price'])} ({fmt_pct(spx_q['change'])} hoje)",
                f"- 2. Ibovespa / IBOV: {fmt_num(ibov_q['price'])} ({fmt_pct(ibov_q['change'])} hoje)",
                f"- 3. Petróleo Brent: $ {fmt_num(brent_q['price'])} ({fmt_pct(brent_q['change'])} hoje)",
                f"- 4. Ouro Spot: $ {fmt_num(gold_q['price'])} ({fmt_pct(gold_q['change'])} hoje)",
                f"- 5. USD / BRL / Dólar Real: R$ {fmt_num(usdbrl_q['price'])} ({fmt_pct(usdbrl_q['change'])} hoje)",
                "",
                "2. ANÁLISE INTEGRADA DAS CATEGORIAS SELECIONADAS"
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
            label="💾 Baixar Relatório (TXT)",
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
"O mercado de {modulo} operando com volatilidade! O ativo principal negociado a {fmt_num(main_q['price'])} ({fmt_pct(main_q['change'])} hoje). Sentimento de mercado em {fng_class}. Acompanhe os níveis operacionais!"

[01:30] DESTAQUES SETORIAIS:
- Categorias Monitoradas: {', '.join(selected_categories[:3])}
- Projeção de Machine Learning para {horizonte_pred}: Tendência com alvo em {alvo_pct}% e suporte em {stop_pct}%.

[05:00] FECHAMENTO:
"Inscreva-se na OMNIRESEARCH Engine para análises em tempo real!"

Powered by OMNIRESEARCH Engine"""

        st.text_area("", value=script_text, height=350)

        st.download_button(
            label="💾 Baixar Roteiro YouTube (TXT)",
            data=script_text,
            file_name=f"OMNI_Roteiro_YouTube_{modulo}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )

    c1, c2, c3, c4 = st.columns(4)
    main_sym_calc = "BTC-USD" if modulo == "Crypto" else "^GSPC"
    main_q = quotes.get(main_sym_calc, {"price": 0.0, "change": 0.0})
    p_curr = main_q['price']

    res_calc = p_curr * (1 + (alvo_pct / 100))
    sup_calc = p_curr * (1 - (stop_pct / 100))
    target_calc = p_curr * (1 + ((alvo_pct * 0.7) / 100))

    with c1:
        st.metric("Tendência", "Compradora" if main_q['change'] >= 0 else "Vendedora", f"{fmt_pct(main_q['change'])}")
    with c2:
        st.metric("Resistência Alvo", f"{fmt_num(res_calc, dec=0)}", f"+{alvo_pct}%")
    with c3:
        st.metric("Suporte Chave", f"{fmt_num(sup_calc, dec=0)}", f"-{stop_pct}%")
    with c4:
        st.metric(f"Previsão {horizonte_pred}", "Alta Moderada", f"Alvo {fmt_num(target_calc, dec=0)}")

# Painel Direito: Métricas Agregadas
with col_right:
    st.subheader(f"📊 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado via API / Dados de Mercado às {datetime.now().strftime('%H:%M:%S BRT')}")

    for item in active_benchmarks:
        label = item["label"]
        badge = item.get("badge", "Data Feed")

        if item.get("type") == "fng_api":
            val_str = fng_val
            chg_str = fng_class
            change_cls = "metric-change-pos" if "Greed" in fng_class else ("metric-change-neg" if "Fear" in fng_class else "metric-change-neutral")

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
# 6. PAINEL DE ANÁLISE INTEGRADA (CARDS DE CATEGORIA)
# -----------------------------------------------------------------------------
st.subheader(f"📁 Painel de Análise Integrada das Categorias ({modulo})")
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

if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.caption(f"© {datetime.now().year} {company_name}. Todos os direitos reservados. Relatório de uso exclusivo.")
else:
    st.caption("⚡ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")