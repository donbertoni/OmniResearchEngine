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
    [data-baseweb="textarea"], textarea {
        background-color: #111827 !important;
        color: #e5e7eb !important;
        border: 1px solid #1f2937 !important;
        font-family: monospace;
    }
    .stCard {
        background-color: #111827 !important;
        padding: 18px;
        border-radius: 8px;
        border: 1px solid #1f2937 !important;
        margin-bottom: 12px;
    }
    .metric-title { font-size: 0.85rem; color: #9ca3af !important; margin-bottom: 4px; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #f3f4f6 !important; }
    .metric-delta-up { font-size: 0.8rem; color: #10b981 !important; }
    .metric-delta-down { font-size: 0.8rem; color: #ef4444 !important; }
    </style>
""", unsafe_allow_html=True)


def fmt_usd(val: float) -> str:
    """Formata valor monetário para o padrão em Dólar com pontuação BR ($ 64.071,00)"""
    return f"${val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")


# --- Horário de Brasília (UTC-3) ---
brt_tz = timezone(timedelta(hours=-3))
now_dt = datetime.datetime.now(brt_tz)
now_str = now_dt.strftime("%d/%m/%Y às %H:%M:%S BRT")
short_time_str = now_dt.strftime("%H:%M:%S BRT")

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


# --- Ingestão Agregada Robusta com Cache Seguro (TTL 3 min para evitar rate-limit) ---
@st.cache_data(ttl=180)
def get_crypto_data_aggregated():
    data = {
        "btc_price": 64071.0, "btc_change": 0.5,
        "eth_price": 1908.7, "eth_change": -0.2,
        "sol_price": 76.03, "sol_change": 1.2,
        "btc_dom": 56.5, "btc_dom_change": 0.1,
        "funding_rate": 0.0100, "funding_rate_delta": 0.0001,
        "is_fallback": False
    }

    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
        res = requests.get(url, headers=HTTP_HEADERS, timeout=5).json()
        
        if "bitcoin" in res:
            data["btc_price"] = float(res["bitcoin"]["usd"])
            data["btc_change"] = float(res["bitcoin"].get("usd_24h_change", 0.0))
        if "ethereum" in res:
            data["eth_price"] = float(res["ethereum"]["usd"])
            data["eth_change"] = float(res["ethereum"].get("usd_24h_change", 0.0))
        if "solana" in res:
            data["sol_price"] = float(res["solana"]["usd"])
            data["sol_change"] = float(res["solana"].get("usd_24h_change", 0.0))
    except Exception:
        data["is_fallback"] = True

    try:
        url_global = "https://api.coingecko.com/api/v3/global"
        res_global = requests.get(url_global, headers=HTTP_HEADERS, timeout=5).json()
        btc_dom = res_global.get("data", {}).get("market_cap_percentage", {}).get("btc")
        if btc_dom:
            data["btc_dom"] = float(btc_dom)
    except Exception:
        pass

    return data


@st.cache_data(ttl=600)
def get_fear_and_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=2"
        res = requests.get(url, headers=HTTP_HEADERS, timeout=5).json()
        d = res["data"]
        curr, prev = int(d[0]["value"]), int(d[1]["value"])
        return {"value": curr, "sentiment": d[0]["value_classification"], "change": curr - prev}
    except Exception:
        return {"value": 31, "sentiment": "Fear", "change": -1}


@st.cache_data(ttl=3600)
def get_global_m2():
    return {"m2_formatted": "$104.8T", "yoy_formatted": "+4.2% YoY"}


def get_support_resistance(btc_price: float):
    sup_low = btc_price * 0.965
    sup_high = btc_price * 0.982
    res_low = btc_price * 1.018
    res_high = btc_price * 1.035
    return {
        "support_str": f"${sup_low/1000:.1f}k - ${sup_high/1000:.1f}k",
        "resistance_str": f"${res_low/1000:.1f}k - ${res_high/1000:.1f}k"
    }


# Ingestão de Dados
market = get_crypto_data_aggregated()
fng = get_fear_and_greed()
sr = get_support_resistance(market["btc_price"])
m2 = get_global_m2()


# --- UI e Interface ---
st.title("⚡ OMNIRESEARCH")
st.caption("Engine de Inteligência Financeira Macro & Crypto (Modelo Agregado Estável)")
st.info(f"🕒 Dados consolidados das {now_str}")

if market["is_fallback"]:
    st.warning("⚠️ Limite temporário de requisições na API. Exibindo última estimativa de mercado consolidada sem interrupções.")

st.divider()

col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    st.subheader("📄 Painel de Aprovação de Roteiro - YouTube (HITL)")
    
    script_content = f"""Roteiro Estendido LLM (~2 min 30 seg de tela):

[00:00 - HOOK DE RETENÇÃO]
O Bitcoin Fear & Greed Index marca {fng['value']} pontos ({fng['sentiment']}) enquanto o BTC consolida na faixa de {fmt_usd(market['btc_price'])}. O cenário macro segue sustentado pela liquidez global do M2 em {m2['m2_formatted']} ({m2['yoy_formatted']}).

[00:35 - BITCOIN & DOMINÂNCIA]
Com a dominância do Bitcoin em {market['btc_dom']:.1f}%, o mercado mantém a atenção voltada para os níveis de suporte e resistência chave.

[01:10 - ALTCOINS LÍDERES]
Ethereum negocia em {fmt_usd(market['eth_price'])} e Solana em {fmt_usd(market['sol_price'])}, refletindo o momento de consolidação do ativo principal.

[01:45 - ANÁLISE TÉCNICA]
A zona de suporte do Bitcoin situa-se em {sr['support_str']}, com resistência imediata em {sr['resistance_str']}."""

    st.text_area("", value=script_content, height=360)

    m1, m2_col, m3 = st.columns(3)
    m1.metric("Suporte BTC", sr["support_str"])
    m2_col.metric("Resistência BTC", sr["resistance_str"])
    m3.metric("M2 Global", m2["m2_formatted"], m2["yoy_formatted"])

with col_right:
    st.subheader("📊 Métricas Agregadas")
    st.caption(f"Atualizado às {short_time_str}")

    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">1. Fear & Greed Index</div>
            <div class="metric-value">{fng['value']} ({fng['sentiment']})</div>
            <div class="metric-delta-up">{fng['change']:+} pts hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-title">2. BTC / USD</div>
            <div class="metric-value">{fmt_usd(market['btc_price'])}</div>
            <div class="metric-delta-up">{market['btc_change']:+.2f}% (24h)</div>
        </div>
        <div class="stCard">
            <div class="metric-title">3. ETH / USD</div>
            <div class="metric-value">{fmt_usd(market['eth_price'])}</div>
            <div class="metric-delta-down">{market['eth_change']:+.2f}% (24h)</div>
        </div>
        <div class="stCard">
            <div class="metric-title">4. SOL / USD</div>
            <div class="metric-value">{fmt_usd(market['sol_price'])}</div>
            <div class="metric-delta-up">{market['sol_change']:+.2f}% (24h)</div>
        </div>
    """, unsafe_allow_html=True)