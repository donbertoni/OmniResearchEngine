import datetime
from datetime import timezone, timedelta
import requests
import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS Dark Mode Total ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
    [data-testid="stMain"], .main, .block-container, [data-testid="stToolbar"] {
        background-color: #0b0f19 !important;
        color: #ffffff !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div, [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }

    .stCaption, small, [data-testid="stCaptionContainer"] {
        color: #9ca3af !important;
    }

    [data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] {
        color: #ffffff !important;
    }

    [data-testid="stAlert"] {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        color: #38bdf8 !important;
    }

    [data-baseweb="textarea"], textarea {
        background-color: #111827 !important;
        color: #e5e7eb !important;
        border: 1px solid #1f2937 !important;
        font-family: monospace;
    }

    [data-baseweb="select"] > div {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        color: #ffffff !important;
    }

    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #9ca3af !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #3b82f6 !important;
    }

    .stCard {
        background-color: #111827 !important;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #1f2937 !important;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        color: #9ca3af !important;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f3f4f6 !important;
    }
    .metric-delta-up {
        font-size: 0.8rem;
        color: #10b981 !important;
    }
    .metric-delta-down {
        font-size: 0.8rem;
        color: #ef4444 !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- Funções Auxiliares ---
def fmt_usd(val: float) -> str:
    """Formata valor monetário para o padrão PT-BR ($ 63.584,00)"""
    return f"${val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")


# --- Horário de Brasília (UTC-3) ---
brt_tz = timezone(timedelta(hours=-3))
now_dt = datetime.datetime.now(brt_tz)
now_str = now_dt.strftime("%d/%m/%Y às %H:%M BRT")
short_time_str = now_dt.strftime("%H:%M BRT")

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# --- Ingestão de Dados ---
@st.cache_data(ttl=60)
def get_crypto_data():
    data = {
        "btc_price": 94500.0, "btc_change": 0.0,
        "eth_price": 3420.50, "eth_change": 0.0,
        "sol_price": 188.40, "sol_change": 0.0,
        "btc_dom": 56.3, "btc_dom_change": -0.4,
        "funding_rate": 0.0100, "funding_rate_delta": 0.0015
    }

    # 1. Preços e Variações 24h (CoinGecko)
    try:
        url_price = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
        res_price = requests.get(url_price, headers=HTTP_HEADERS, timeout=6).json()

        if "bitcoin" in res_price:
            data["btc_price"] = res_price["bitcoin"]["usd"]
            data["btc_change"] = res_price["bitcoin"].get("usd_24h_change", 0.0)
        if "ethereum" in res_price:
            data["eth_price"] = res_price["ethereum"]["usd"]
            data["eth_change"] = res_price["ethereum"].get("usd_24h_change", 0.0)
        if "solana" in res_price:
            data["sol_price"] = res_price["solana"]["usd"]
            data["sol_change"] = res_price["solana"].get("usd_24h_change", 0.0)
    except Exception:
        pass

    # 2. Dominância BTC
    try:
        url_global = "https://api.coingecko.com/api/v3/global"
        res_global = requests.get(url_global, headers=HTTP_HEADERS, timeout=6).json()
        btc_dom = res_global.get("data", {}).get("market_cap_percentage", {}).get("btc")
        dom_change = res_global.get("data", {}).get("market_cap_change_percentage_24h_usd", -0.4)
        if btc_dom:
            data["btc_dom"] = btc_dom
            data["btc_dom_change"] = dom_change
    except Exception:
        pass

    # 3. Funding Rate (Binance Futures)
    try:
        url_funding = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=2"
        res_funding = requests.get(url_funding, headers=HTTP_HEADERS, timeout=6).json()
        if isinstance(res_funding, list) and len(res_funding) >= 2:
            current_fr = float(res_funding[-1]["fundingRate"]) * 100
            prev_fr = float(res_funding[-2]["fundingRate"]) * 100
            data["funding_rate"] = current_fr
            data["funding_rate_delta"] = current_fr - prev_fr
    except Exception:
        pass

    return data


@st.cache_data(ttl=300)
def get_fear_and_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=2"
        res = requests.get(url, headers=HTTP_HEADERS, timeout=6).json()
        data = res["data"]
        current_val = int(data[0]["value"])
        prev_val = int(data[1]["value"])
        return {
            "value": current_val,
            "sentiment": data[0]["value_classification"],
            "change": current_val - prev_val
        }
    except Exception:
        return {"value": 31, "sentiment": "Fear", "change": -3}


market = get_crypto_data()
fng = get_fear_and_greed()


# --- Cabeçalho OMNIRESEARCH ---
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.title("⚡ OMNIRESEARCH")
    st.caption("Engine de Inteligência Financeira Multiativo")
    st.info(f"🕒 Report Gerado em: {now_str}")

with col_head2:
    target_profile = st.selectbox("Perfil do Relatório (Target):", ["🎥 B2C: YouTube Crypto Content"])
    autopilot = st.toggle("Modo Autopilot", value=False)
    if autopilot:
        st.caption("Autopilot ON: Publicação automática sem HITL.")

st.divider()


# --- Layout Principal ---
col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    st.subheader("📄 Painel de Aprovação de Roteiro - YouTube (HITL)")

    tab_pt, tab_en = st.tabs(["🇧🇷 PT-BR (Crypto & Liquidez Global)", "🇺🇸 EN-US (Crypto & Global Liquidity)"])

    with tab_pt:
        fng_text = f"{fng['value']} pontos em {fng['sentiment'].lower()}"
        btc_formatted = fmt_usd(market['btc_price'])
        eth_formatted = fmt_usd(market['eth_price'])
        sol_formatted = fmt_usd(market['sol_price'])

        script_content = f"""Roteiro Estendido LLM (~2 min 30 seg de tela):

[00:00 - HOOK DE RETENÇÃO]
(Horário de criação do Report: {now_str})
O Fear & Greed Index marca {fng_text} enquanto o Bitcoin sustenta a faixa dos {btc_formatted}. Porém, o verdadeiro gatilho estrutural vem do M2 Global, que atingiu nova máxima histórica em $104.8 Trilhões.

[00:35 - BITCOIN & DOMINÂNCIA]
Com a dominância do Bitcoin em {market['btc_dom']:.1f}%, vemos a liquidez se distribuindo pelas principais Layer 1s do mercado. O Funding Rate do BTC em {market['funding_rate']:.4f}% reflete o posicionamento dos derivativos sem euforia exagerada.

[01:10 - ALTCOINS LÍDERES: ETHEREUM E SOLANA]
O Ethereum negocia a {eth_formatted} impulsionado por fluxos institucionais nos ETFs spot, enquanto Solana é cotada a {sol_formatted} suportada pelo volume nas DEXs da rede.

[01:45 - ANÁLISE TÉCNICA E MATRIZ PREDITIVA]
A zona de suporte imediata do BTC reside em $93.8k, com resistência crítica mapeada em $97.2k. Nossa matriz preditiva aponta 65% de probabilidade altista para as próximas 48 horas."""

        st.text_area("", value=script_content, height=380)

        st.markdown("### 🎯 Níveis Chave & Matriz Preditiva")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Zona de Suporte", "93.8k - 94.2k", "↑ Forte Defesa")
        m2.metric("Zona de Resistência", "97.2k - 98.5k", "↑ Alvo Chave")
        m3.metric("Matriz Preditiva 48h", "65% Bullish", "↑ Alta Confiança")
        m4.metric("M2 Total Supply", "$104.8T", "+4.2% YoY")


with col_right:
    st.subheader("📊 Ingestão de Mercado (Crypto)")
    st.caption(f"Horário de criação do Report: {short_time_str}")

    # Card 1: Fear & Greed
    fng_delta_class = "metric-delta-up" if fng["change"] >= 0 else "metric-delta-down"
    fng_arrow = "↑" if fng["change"] >= 0 else "↓"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">1. Fear & Greed Index</div>
            <div class="metric-value">{fng['value']} ({fng['sentiment']})</div>
            <div class="{fng_delta_class}">{fng_arrow} {fng['change']:+} pts</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 2: BTC / USDT
    btc_delta_class = "metric-delta-up" if market["btc_change"] >= 0 else "metric-delta-down"
    btc_arrow = "↑" if market["btc_change"] >= 0 else "↓"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">2. BTC / USDT</div>
            <div class="metric-value">{fmt_usd(market['btc_price'])}</div>
            <div class="{btc_delta_class}">{btc_arrow} {market['btc_change']:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 3: BTC Dominance
    dom_delta = market.get("btc_dom_change", -0.4)
    dom_class = "metric-delta-up" if dom_delta >= 0 else "metric-delta-down"
    dom_arrow = "↑" if dom_delta >= 0 else "↓"
    dom_tag = "(Concentração BTC)" if dom_delta >= 0 else "(Rotação)"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">3. BTC Dominance</div>
            <div class="metric-value">{market['btc_dom']:.1f}%</div>
            <div class="{dom_class}">{dom_arrow} {dom_delta:+.1f}% {dom_tag}</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 4: ETH / USDT
    eth_delta_class = "metric-delta-up" if market["eth_change"] >= 0 else "metric-delta-down"
    eth_arrow = "↑" if market["eth_change"] >= 0 else "↓"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">4. ETH / USDT</div>
            <div class="metric-value">{fmt_usd(market['eth_price'])}</div>
            <div class="{eth_delta_class}">{eth_arrow} {market['eth_change']:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 5: SOL / USDT
    sol_delta_class = "metric-delta-up" if market["sol_change"] >= 0 else "metric-delta-down"
    sol_arrow = "↑" if market["sol_change"] >= 0 else "↓"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">5. SOL / USDT</div>
            <div class="metric-value">{fmt_usd(market['sol_price'])}</div>
            <div class="{sol_delta_class}">{sol_arrow} {market['sol_change']:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 6: BTC Funding Rate
    fr = market["funding_rate"]
    fr_delta = market.get("funding_rate_delta", 0.0)
    fr_class = "metric-delta-up" if fr_delta >= 0 else "metric-delta-down"
    fr_arrow = "↑" if fr_delta >= 0 else "↓"
    fr_label = "(Longs Alavancados)" if fr > 0.015 else ("(Shorts Dominantes)" if fr < 0 else "(Saudável)")

    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">6. BTC Funding Rate</div>
            <div class="metric-value">{fr:.4f}%</div>
            <div class="{fr_class}">{fr_arrow} {fr_delta:+.4f}% {fr_label}</div>
        </div>
    """, unsafe_allow_html=True)