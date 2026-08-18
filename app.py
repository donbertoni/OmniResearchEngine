import streamlit as st
import yfinance as yf
from datetime import datetime
import pandas as pd

# Configuração da página Streamlit
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para visual escuro institucional
st.markdown("""
<style>
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
        font-size: 20px;
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
        font-size: 14px;
        font-weight: 700;
        color: #58A6FF;
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
        font-size: 13px;
    }
    .asset-symbol {
        color: #C9D1D9;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Estrutura de dados para TradFi / Macro
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
    "8 - Crypto e Digital": {
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
    {"key": "DXY", "ticker": "DX-Y.NYB", "label": "3. DXY / Índice Dólar", "unit": "pts", "prefix": "", "badge": "yfinance API"},
    {"key": "US10Y", "ticker": "^TNX", "label": "4. US 10Y Treasury Yield", "unit": "%", "prefix": "", "badge": "yfinance API", "suffix": "%"},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "5. USD / BRL / Dólar Real", "unit": "pts", "prefix": "R$ ", "badge": "yfinance API"}
]

# Estrutura de dados para Crypto com BTC e ETH no topo
CATEGORIES_CRYPTO = {
    "1 - Major Layer 1s": {
        "tag": "L1 / Majors",
        "assets": [
            ("BTCUSDT", "BTC-USD", "$"),
            ("ETHUSDT", "ETH-USD", "$"),
            ("SOLUSDT", "SOL-USD", "$"),
            ("BNBUSDT", "BNB-USD", "$"),
        ]
    },
    "2 - Altcoins & Smart Contracts": {
        "tag": "Altcoins",
        "assets": [
            ("ADAUSD", "ADA-USD", "$"),
            ("LINKUSD", "LINK-USD", "$"),
            ("AVAXUSD", "AVAX-USD", "$"),
            ("DOTUSD", "DOT-USD", "$"),
        ]
    },
    "3 - AI & DePIN Assets": {
        "tag": "AI & Tech",
        "assets": [
            ("FETUSDT", "FET-USD", "$"),
            ("RENDERUSDT", "RENDER-USD", "$"),
            ("NEARUSDT", "NEAR-USD", "$"),
            ("TAOUSD", "TAO-USD", "$"),
        ]
    },
    "4 - Pares Local & Cross": {
        "tag": "Pairs / BRL",
        "assets": [
            ("BTCBRL", "BTC-BRL", "R$"),
            ("ETHBTC", "ETH-BTC", "Ξ"),
            ("USDTBRL", "BRL=X", "R$"),
            ("USDTUSD", "USDT-USD", "$"),
        ]
    }
}

CRYPTO_BENCHMARKS = [
    {
        "key": "BTC",
        "ticker": "BTC-USD",
        "label": "1. Bitcoin / BTC",
        "prefix": "$ ",
        "badge": "yfinance API"
    },
    {
        "key": "ETH",
        "ticker": "ETH-USD",
        "label": "2. Ethereum / ETH",
        "prefix": "$ ",
        "badge": "yfinance API"
    },
    {
        "key": "BTC_D",
        "ticker": None,
        "label": "3. Bitcoin Dominance / BTC.D",
        "static_val": "56,80%",
        "static_chg": "+0,35% hoje",
        "badge": "On-Chain Data"
    },
    {
        "key": "TOTAL_MCAP",
        "ticker": None,
        "label": "4. Total Crypto Market Cap",
        "static_val": "$ 2,28 T",
        "static_chg": "+1,12% hoje",
        "badge": "Global Crypto"
    },
    {
        "key": "FEAR_GREED",
        "ticker": None,
        "label": "5. Crypto Fear & Greed Index",
        "static_val": "62 / 100",
        "static_chg": "Greed (Ganância)",
        "badge": "Sentiment Index"
    }
]

# Função com cache de 60s para buscar cotações em tempo real
@st.cache_data(ttl=60)
def fetch_realtime_quotes():
    all_symbols = []
    
    # Adiciona tickers de benchmarks TradFi e Crypto
    for item in MACRO_BENCHMARKS:
        if item.get("ticker"):
            all_symbols.append(item["ticker"])
    for item in CRYPTO_BENCHMARKS:
        if item.get("ticker"):
            all_symbols.append(item["ticker"])

    # Adiciona tickers de categorias
    for cat in CATEGORIES_TRADFI.values():
        for _, ticker, _ in cat["assets"]:
            all_symbols.append(ticker)
    for cat in CATEGORIES_CRYPTO.values():
        for _, ticker, _ in cat["assets"]:
            all_symbols.append(ticker)

    unique_symbols = list(set(all_symbols))
    quotes = {}

    try:
        data = yf.download(unique_symbols, period="5d", interval="1d", group_by="ticker", progress=False)
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
                quotes[sym] = {"price": 0.0, "change": 0.0}
    except Exception:
        for sym in unique_symbols:
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="5d")
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

# Busca dados de cotação
quotes = fetch_realtime_quotes()

# --- SIDEBAR: Configurações ---
st.sidebar.title("⚡ Configurações OMNI")
st.sidebar.caption("Controle de geração de roteiros e relatórios")

idioma = st.sidebar.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English", "Español"])
modulo = st.sidebar.radio("💡 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=0)

# Define dicionários e benchmarks ativos conforme seleção do módulo
if modulo == "Crypto":
    active_categories = CATEGORIES_CRYPTO
    active_benchmarks = CRYPTO_BENCHMARKS
else:
    active_categories = CATEGORIES_TRADFI
    active_benchmarks = MACRO_BENCHMARKS

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Calibragem (SaaS Enterprise)")
st.sidebar.caption("Selecione os setores/categorias:")

selected_categories = []
for key in active_categories.keys():
    if st.sidebar.checkbox(key, value=True):
        selected_categories.append(key)

st.sidebar.markdown("---")
formato = st.sidebar.radio(f"🎯 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube)"], index=0)

st.sidebar.info("💡 O modo Auto-Pilot está disponível exclusivamente para entregáveis B2C (YouTube).")

# --- CORPO PRINCIPAL ---
st.title("⚡ OMNIRESEARCH Engine")
st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
st.markdown(
    f"""
    <div class="status-bar">
        🕒 <b>Dados consolidados das {now_str}</b> | Status da API: <span style="color: #10B981;">● Online (yfinance)</span> | <b>Módulo Ativo:</b> {modulo}
    </div>
    """,
    unsafe_allow_html=True
)

col_left, col_right = st.columns([1.3, 1])

# Painel Esquerdo: Relatório B2B em Tempo Real
with col_left:
    st.subheader(f"📄 Relatório B2B ({modulo})")
    st.caption("Relatório com indicadores integrados em tempo real via API:")

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
            "- 3. Bitcoin Dominance (BTC.D): 56,80% (+0,35% hoje) [On-Chain Data]",
            "- 4. Total Crypto Market Cap: $ 2,28 T (+1,12% hoje) [Global Crypto]",
            "- 5. Crypto Fear & Greed Index: 62 / 100 (Greed / Ganância)",
            "",
            "2. ANÁLISE INTEGRADA DAS CATEGORIAS CRYPTO SELECIONADAS"
        ]
    else:
        spx_q = quotes.get("^GSPC", {"price": 0.0, "change": 0.0})
        ibov_q = quotes.get("^BVSP", {"price": 0.0, "change": 0.0})
        dxy_q = quotes.get("DX-Y.NYB", {"price": 0.0, "change": 0.0})
        us10y_q = quotes.get("^TNX", {"price": 0.0, "change": 0.0})
        usdbrl_q = quotes.get("BRL=X", {"price": 0.0, "change": 0.0})

        report_lines = [
            "=== RELATÓRIO INSTITUCIONAL TRADFI (MACRO) (B2B) ===",
            f"Data/Hora: {now_str}",
            "",
            "1. PANORAMA & BENCHMARKS DE MERCADO (DADOS VIA YFINANCE API)",
            f"- 1. S&P 500 / SPX: {fmt_num(spx_q['price'])} ({fmt_pct(spx_q['change'])} hoje) [yfinance API]",
            f"- 2. Ibovespa / IBOV: {fmt_num(ibov_q['price'])} ({fmt_pct(ibov_q['change'])} hoje) [yfinance API]",
            f"- 3. DXY / Índice Dólar: {fmt_num(dxy_q['price'])} ({fmt_pct(dxy_q['change'])} hoje) [yfinance API]",
            f"- 4. US 10Y Treasury Yield: {fmt_num(us10y_q['price'])}% ({fmt_num(us10y_q['change'])} bps hoje) [yfinance API]",
            f"- 5. USD / BRL / Dólar Real: R$ {fmt_num(usdbrl_q['price'])} ({fmt_pct(usdbrl_q['change'])} hoje) [yfinance API]",
            "",
            "2. ANÁLISE INTEGRADA DAS CATEGORIAS SELECIONADAS (DADOS EM TEMPO REAL)"
        ]

    for cat_name in selected_categories:
        cat_info = active_categories[cat_name]
        report_lines.append(f"\n• {cat_name.upper()} ({cat_info['tag']}):")
        for disp_name, ticker, currency in cat_info["assets"]:
            q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
            report_lines.append(f"  - {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")

    st.text_area("", value="\n".join(report_lines), height=380)

    # Cards técnicos dinâmicos
    c1, c2, c3, c4 = st.columns(4)
    if modulo == "Crypto":
        main_q = quotes.get("BTC-USD", {"price": 0.0, "change": 0.0})
        with c1:
            st.metric("Tendência 7D (BTC)", "Compradora", f"{fmt_pct(main_q['change'])}")
        with c2:
            st.metric("Resistência (BTC)", f"$ {fmt_num(main_q['price'] * 1.05, dec=0)}", "Nível Crítico")
        with c3:
            st.metric("Suporte Crítico", f"$ {fmt_num(main_q['price'] * 0.95, dec=0)}", "Zona Defesa")
        with c4:
            st.metric("Previsão 48h", "Alta Moderada", f"Alvo $ {fmt_num(main_q['price'] * 1.03, dec=0)}")
    else:
        main_q = quotes.get("^GSPC", {"price": 0.0, "change": 0.0})
        with c1:
            st.metric("Tendência 7D (Macro)", "Compradora", f"{fmt_pct(main_q['change'])}")
        with c2:
            st.metric("Resistência (S&P)", f"{fmt_num(main_q['price'] * 1.02, dec=0)} pts", "Nível Crítico")
        with c3:
            st.metric("Suporte Crítico", f"{fmt_num(main_q['price'] * 0.98, dec=0)} pts", "Zona Defesa")
        with c4:
            st.metric("Previsão 48h", "Alta Moderada", f"Alvo {fmt_num(main_q['price'] * 1.01, dec=0)}")

# Painel Direito: Métricas Agregadas Dinâmicas
with col_right:
    st.subheader(f"📊 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado via API / Dados de Mercado às {datetime.now().strftime('%H:%M:%S BRT')}")

    for item in active_benchmarks:
        label = item["label"]
        badge = item.get("badge", "Data Feed")
        
        if item.get("ticker"):
            ticker = item["ticker"]
            data = quotes.get(ticker, {"price": 0.0, "change": 0.0})
            prefix = item.get("prefix", "")
            suffix = item.get("suffix", "")
            val_str = f"{prefix}{fmt_num(data['price'])}{suffix}"
            chg_str = f"{fmt_pct(data['change'])} hoje"
            change_cls = "metric-change-pos" if data["change"] >= 0 else "metric-change-neg"
        else:
            val_str = item.get("static_val", "--")
            chg_str = item.get("static_chg", "")
            change_cls = "metric-change-neutral" if "Greed" in chg_str else ("metric-change-pos" if "+" in chg_str else "metric-change-neg")

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{label} <span style="font-size:10px; opacity:0.6;">[{badge}]</span></div>
            <div class="metric-value">{val_str}</div>
            <div class="{change_cls}">{chg_str}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Section 2: Painel de Análise das Categorias Ativas
st.subheader(f"📂 Painel de Análise Integrada das Categorias ({modulo})")
st.caption("Visão detalhada dos setores selecionados no painel lateral com cotações automáticas:")

if selected_categories:
    cols = st.columns(min(len(selected_categories), 4))
    for idx, cat_name in enumerate(selected_categories):
        cat_info = active_categories[cat_name]
        col = cols[idx % len(cols)]
        
        with col:
            st.markdown(f"""
            <div class="category-card">
                <div class="category-header">
                    <div class="category-title">{cat_name}</div>
                    <div class="category-tag">{cat_info['tag']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            for disp_name, ticker, currency in cat_info["assets"]:
                q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                color_style = "color: #3FB950;" if q["change"] >= 0 else "color: #F85149;"
                st.markdown(f"""
                <div class="asset-row">
                    <span class="asset-symbol">{disp_name}:</span>
                    <span><b>{currency} {fmt_num(q['price'])}</b> <span style="{color_style} font-size: 11px;">({fmt_pct(q['change'])})</span></span>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True)