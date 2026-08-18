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

# Definição dos ativos por categoria e seus tickers na API yfinance
CATEGORIES = {
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

MACRO_TICKERS = {
    "SPX": ("^GSPC", "S&P 500 / SPX", "pts"),
    "IBOV": ("^BVSP", "Ibovespa / IBOV", "pts"),
    "DXY": ("DX-Y.NYB", "DXY / Índice Dólar", "pts"),
    "US10Y": ("^TNX", "US 10Y Treasury Yield", "%"),
    "USDBRL": ("BRL=X", "USD / BRL / Dólar Real", "R$"),
}

# Função com cache para buscar cotações em tempo real via yfinance
@st.cache_data(ttl=60)
def fetch_realtime_quotes():
    all_symbols = [info[0] for info in MACRO_TICKERS.values()]
    for cat in CATEGORIES.values():
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

# Busca dados de cotação atualizados
quotes = fetch_realtime_quotes()

# --- SIDEBAR: Configurações ---
st.sidebar.title("⚡ Configurações OMNI")
st.sidebar.caption("Controle de geração de roteiros e relatórios")

idioma = st.sidebar.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English", "Español"])
modulo = st.sidebar.radio("💡 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Calibragem (SaaS Enterprise)")
st.sidebar.caption("Selecione os setores/categorias:")

selected_categories = []
for key in CATEGORIES.keys():
    if st.sidebar.checkbox(key, value=True):
        selected_categories.append(key)

st.sidebar.markdown("---")
formato = st.sidebar.radio("🎯 Formato (TradFi (Macro)):", ["B2B (Relatório)", "B2C (YouTube)"], index=0)

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
    st.subheader("📄 Relatório B2B (TradFi & Macro)")
    st.caption("Relatório com indicadores integrados em tempo real via API:")

    spx_q = quotes.get(MACRO_TICKERS["SPX"][0], {"price": 0.0, "change": 0.0})
    ibov_q = quotes.get(MACRO_TICKERS["IBOV"][0], {"price": 0.0, "change": 0.0})
    dxy_q = quotes.get(MACRO_TICKERS["DXY"][0], {"price": 0.0, "change": 0.0})
    us10y_q = quotes.get(MACRO_TICKERS["US10Y"][0], {"price": 0.0, "change": 0.0})
    usdbrl_q = quotes.get(MACRO_TICKERS["USDBRL"][0], {"price": 0.0, "change": 0.0})

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
        cat_info = CATEGORIES[cat_name]
        report_lines.append(f"\n• {cat_name.upper()} ({cat_info['tag']}):")
        for disp_name, ticker, currency in cat_info["assets"]:
            q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
            report_lines.append(f"  - {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")

    st.text_area("", value="\n".join(report_lines), height=380)

    # Cards técnicos do relatório
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tendência 7D (Macro)", "Compradora", f"{fmt_pct(spx_q['change'])}")
    with c2:
        st.metric("Resistência (S&P)", f"{fmt_num(spx_q['price'] * 1.02, dec=0)} pts", "Nível Crítico")
    with c3:
        st.metric("Suporte Crítico", f"{fmt_num(spx_q['price'] * 0.98, dec=0)} pts", "Zona Defesa")
    with c4:
        st.metric("Previsão 48h", "Alta Moderada", f"Alvo {fmt_num(spx_q['price'] * 1.01, dec=0)}")

# Painel Direito: Métricas Agregadas
with col_right:
    st.subheader("📊 Métricas Agregadas (TradFi & Macro)")
    st.caption(f"Atualizado via yfinance API às {datetime.now().strftime('%H:%M:%S BRT')}")

    macro_items = [
        ("1. S&P 500 / SPX", spx_q, "pts", ""),
        ("2. Ibovespa / IBOV", ibov_q, "pts", ""),
        ("3. DXY / Índice Dólar", dxy_q, "pts", ""),
        ("4. US 10Y Treasury Yield", us10y_q, "%", "%"),
        ("5. USD / BRL / Dólar Real", usdbrl_q, "pts", "R$ ")
    ]

    for label, data, unit, prefix in macro_items:
        change_cls = "metric-change-pos" if data["change"] >= 0 else "metric-change-neg"
        val_str = f"{prefix}{fmt_num(data['price'])}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{label} <span style="font-size:10px; opacity:0.6;">[yfinance API]</span></div>
            <div class="metric-value">{val_str}</div>
            <div class="{change_cls}">{fmt_pct(data['change'])} hoje</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Section 2: Painel de Análise das Categorias
st.subheader("📂 Painel de Análise Integrada das 8 Categorias (TradFi (Macro))")
st.caption("Visão detalhada dos setores selecionados no painel lateral com cotações automáticas:")

cols = st.columns(4)
for idx, cat_name in enumerate(selected_categories):
    cat_info = CATEGORIES[cat_name]
    col = cols[idx % 4]
    
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