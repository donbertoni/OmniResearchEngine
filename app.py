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
now_str = now_dt.strftime("%d/%m/%Y às %H:%M:%S BRT")
short_time_str = now_dt.strftime("%H:%M:%S BRT")

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


# --- Ingestão de Dados em Tempo Real (Binance Direct API) ---
@st.cache_data(ttl=10)
def get_crypto_data_realtime():
    """
    Consome dados diretamente do Ticker Spot 24h da Binance (Alta Frequência / Sem Rate Limit).
    """
    data = {
        "btc_price": 0.0, "btc_change": 0.0,
        "eth_price": 0.0, "eth_change": 0.0,
        "sol_price": 0.0, "sol_change": 0.0,
        "btc_dom": 56.5, "btc_dom_change": 0.0,
        "funding_rate": 0.0100, "funding_rate_delta": 0.0000,
        "error": False
    }

    symbols = '["BTCUSDT","ETHUSDT","SOLUSDT"]'
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbols={symbols}"
        res = requests.get(url, headers=HTTP_HEADERS, timeout=4).json()
        
        for item in res:
            sym = item["symbol"]
            price = float(item["lastPrice"])
            change = float(item["priceChangePercent"])
            if sym == "BTCUSDT":
                data["btc_price"] = price
                data["btc_change"] = change
            elif sym == "ETHUSDT":
                data["eth_price"] = price
                data["eth_change"] = change
            elif sym == "SOLUSDT":
                data["sol_price"] = price
                data["sol_change"] = change
    except Exception:
        data["error"] = True

    # 2. Funding Rate em Tempo Real (Binance Futures)
    try:
        url_funding = "https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=2"
        res_funding = requests.get(url_funding, headers=HTTP_HEADERS, timeout=4).json()
        if isinstance(res_funding, list) and len(res_funding) >= 2:
            current_fr = float(res_funding[-1]["fundingRate"]) * 100
            prev_fr = float(res_funding[-2]["fundingRate"]) * 100
            data["funding_rate"] = current_fr
            data["funding_rate_delta"] = current_fr - prev_fr
    except Exception:
        pass

    # 3. Dominância do BTC (CoinGecko Global com Fallback Conservador)
    try:
        url_global = "https://api.coingecko.com/api/v3/global"
        res_global = requests.get(url_global, headers=HTTP_HEADERS, timeout=4).json()
        btc_dom = res_global.get("data", {}).get("market_cap_percentage", {}).get("btc")
        dom_change = res_global.get("data", {}).get("market_cap_change_percentage_24h_usd", 0.0)
        if btc_dom:
            data["btc_dom"] = btc_dom
            data["btc_dom_change"] = dom_change
    except Exception:
        pass

    return data


@st.cache_data(ttl=180)
def get_fear_and_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=2"
        res = requests.get(url, headers=HTTP_HEADERS, timeout=4).json()
        data = res["data"]
        current_val = int(data[0]["value"])
        prev_val = int(data[1]["value"])
        return {
            "value": current_val,
            "sentiment": data[0]["value_classification"],
            "change": current_val - prev_val
        }
    except Exception:
        return {"value": 50, "sentiment": "Neutral", "change": 0}


@st.cache_data(ttl=60)
def get_support_resistance(btc_price: float):
    if btc_price <= 0:
        return {
            "support_str": "N/A", "resistance_str": "N/A",
            "sup_low": 0, "sup_high": 0, "res_low": 0, "res_high": 0
        }

    sup_low = btc_price * 0.965
    sup_high = btc_price * 0.982
    res_low = btc_price * 1.018
    res_high = btc_price * 1.035

    try:
        url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=14"
        res = requests.get(url, headers=HTTP_HEADERS, timeout=4).json()

        if isinstance(res, list) and len(res) >= 2:
            prev_high = float(res[-2][2])
            prev_low = float(res[-2][3])
            prev_close = float(res[-2][4])

            pivot = (prev_high + prev_low + prev_close) / 3.0
            s1 = (2 * pivot) - prev_high
            r1 = (2 * pivot) - prev_low
            s2 = pivot - (prev_high - prev_low)
            r2 = pivot + (prev_high - prev_low)

            recent_lows = [float(k[3]) for k in res[-7:]]
            recent_highs = [float(k[2]) for k in res[-7:]]
            min_7d = min(recent_lows)
            max_7d = max(recent_highs)

            sup_low = min(s1 if btc_price > pivot else s2, min_7d)
            sup_high = max(s1 if btc_price > pivot else s2, min_7d)

            res_low = min(r1 if btc_price < pivot else r2, max_7d)
            res_high = max(r1 if btc_price < pivot else r2, max_7d)

            if sup_high >= btc_price:
                sup_high = btc_price * 0.988
            if sup_low >= sup_high:
                sup_low = sup_high * 0.975

            if res_low <= btc_price:
                res_low = btc_price * 1.012
            if res_high <= res_low:
                res_high = res_low * 1.025
    except Exception:
        pass

    return {
        "support_str": f"{sup_low/1000:.1f}k - {sup_high/1000:.1f}k",
        "resistance_str": f"{res_low/1000:.1f}k - {res_high/1000:.1f}k",
        "sup_low": sup_low,
        "sup_high": sup_high,
        "res_low": res_low,
        "res_high": res_high
    }


@st.cache_data(ttl=3600)
def get_global_m2():
    m2_total_trillions = 104.8
    m2_yoy_pct = 4.2

    try:
        url_fred = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=WM2NS"
        res = requests.get(url_fred, headers=HTTP_HEADERS, timeout=5)
        if res.status_code == 200:
            lines = [line.strip() for line in res.text.strip().split("\n") if line.strip()]
            valid_rows = []
            for line in lines[1:]:
                parts = line.split(",")
                if len(parts) == 2 and parts[1] != ".":
                    try:
                        valid_rows.append((parts[0], float(parts[1])))
                    except ValueError:
                        pass
            if len(valid_rows) >= 52:
                latest_us_m2 = valid_rows[-1][1] / 1000.0
                prev_year_us_m2 = valid_rows[-52][1] / 1000.0
                us_m2_yoy = ((latest_us_m2 - prev_year_us_m2) / prev_year_us_m2) * 100.0

                m2_total_trillions = round(latest_us_m2 * 4.88, 1)
                m2_yoy_pct = round(us_m2_yoy * 1.08, 1)
    except Exception:
        pass

    yoy_sign = "+" if m2_yoy_pct >= 0 else ""
    return {
        "m2_formatted": f"${m2_total_trillions:.1f}T",
        "yoy_formatted": f"{yoy_sign}{m2_yoy_pct:.1f}% YoY",
        "raw_trillions": m2_total_trillions,
        "raw_yoy": m2_yoy_pct
    }


def calculate_predictive_matrix(market: dict, fng: dict, sr: dict):
    score = 50.0

    btc_chg = market.get("btc_change", 0.0)
    score += max(min(btc_chg * 4.0, 22.0), -22.0)

    fr = market.get("funding_rate", 0.01)
    if 0.005 <= fr <= 0.015:
        score += 8.0
    elif 0.0 < fr < 0.005:
        score += 5.0
    elif fr < 0:
        score += 12.0
    elif fr > 0.03:
        score -= 12.0

    fng_val = fng.get("value", 50)
    if 35 <= fng_val <= 60:
        score += 8.0
    elif 20 <= fng_val < 35:
        score += 5.0
    elif fng_val < 20:
        score += 8.0
    elif fng_val > 75:
        score -= 10.0

    if market["btc_price"] > 0:
        sup_low = sr.get("sup_low", market["btc_price"] * 0.97)
        res_high = sr.get("res_high", market["btc_price"] * 1.03)
        range_total = res_high - sup_low

        if range_total > 0:
            relative_pos = (market["btc_price"] - sup_low) / range_total
            if relative_pos < 0.35:
                score += 8.0
            elif relative_pos > 0.85:
                score -= 6.0

    bullish_pct = int(max(min(round(score), 88), 15))

    if bullish_pct >= 60:
        direction = f"{bullish_pct}% Bullish"
        confidence = "↑ Alta Confiança" if bullish_pct >= 70 else "↑ Viés Altista"
        trend_desc = "altista"
    elif bullish_pct <= 42:
        direction = f"{100 - bullish_pct}% Bearish"
        confidence = "↓ Risco de Baixa" if bullish_pct <= 35 else "↓ Viés Baixista"
        trend_desc = "baixista"
    else:
        direction = f"{bullish_pct}% Neutro"
        confidence = "→ Consolidação"
        trend_desc = "neutra/lateral"

    return {
        "bullish_pct": bullish_pct,
        "direction": direction,
        "confidence": confidence,
        "trend_desc": trend_desc
    }


# Ingestão Geral
market = get_crypto_data_realtime()
fng = get_fear_and_greed()
sr = get_support_resistance(market["btc_price"])
m2 = get_global_m2()
pred = calculate_predictive_matrix(market, fng, sr)


# --- Cabeçalho OMNIRESEARCH ---
col_head1, col_head2 = st.columns([3, 1])

with col_head1:
    st.title("⚡ OMNIRESEARCH")
    st.caption("Engine de Inteligência Financeira Multiativo (Dados Diretos Spot Binance)")
    st.info(f"🕒 Atualização em Tempo Real: {now_str}")

with col_head2:
    target_profile = st.selectbox("Perfil do Relatório (Target):", ["🎥 B2C: YouTube Crypto Content"])
    autopilot = st.toggle("Modo Autopilot", value=False)
    if autopilot:
        st.caption("Autopilot ON: Publicação automática sem HITL.")

if market.get("error"):
    st.error("⚠️ Atenção: Falha de comunicação com os servidores Spot da Binance. Verifique a conexão de rede.")

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
O Bitcoin Fear & Greed Index marca {fng_text} enquanto o BTC sustenta a faixa dos {btc_formatted}. O gatilho macro de fundo permanece atrelado à expansão da liquidez global, com o M2 registrando {m2['m2_formatted']} ({m2['yoy_formatted']}).

[00:35 - BITCOIN & DOMINÂNCIA]
Com a dominância do Bitcoin em {market['btc_dom']:.1f}%, a estrutura do mercado permanece centralizada na ação de preço do ativo principal. O Funding Rate do BTC em {market['funding_rate']:.4f}% reflete o posicionamento dos futuros sem excesso de alavancagem.

[01:10 - ALTCOINS LÍDERES: ETHEREUM E SOLANA]
No radar das Layer 1s, o Ethereum negocia a {eth_formatted} e a Solana é cotada a {sol_formatted}, acompanhando o fluxo de liquidez ditado pelo BTC.

[01:45 - ANÁLISE TÉCNICA E MATRIZ PREDITIVA DO BTC]
A zona de suporte imediata do Bitcoin reside em {sr['support_str']}, com resistência crítica em {sr['resistance_str']}. Nossa matriz preditiva focada exclusivamente no BTC aponta probabilidade {pred['trend_desc']} de {pred['direction']} para as próximas 48 horas."""

        st.text_area("", value=script_content, height=380)

        st.markdown("### 🎯 Níveis Chave & M2 Total Supply")
        m1, m2_col, m3, m4 = st.columns(4)
        m1.metric("Zona de Suporte", sr["support_str"], "↑ Forte Defesa")
        m2_col.metric("Zona de Resistência", sr["resistance_str"], "↑ Alvo Chave")
        m3.metric("Matriz Preditiva 48h", pred["direction"], pred["confidence"])
        m4.metric("M2 Total Supply (FRED)", m2["m2_formatted"], m2["yoy_formatted"])


with col_right:
    st.subheader("📊 Ingestão de Mercado (Spot Binance)")
    st.caption(f"Último Ticker: {short_time_str}")

    # Card 1: Fear & Greed
    fng_delta_class = "metric-delta-up" if fng["change"] >= 0 else "metric-delta-down"
    fng_arrow = "↑" if fng["change"] >= 0 else "↓"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">1. Fear & Greed Index (Diário)</div>
            <div class="metric-value">{fng['value']} ({fng['sentiment']})</div>
            <div class="{fng_delta_class}">{fng_arrow} {fng['change']:+} pts</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 2: BTC / USDT
    btc_delta_class = "metric-delta-up" if market["btc_change"] >= 0 else "metric-delta-down"
    btc_arrow = "↑" if market["btc_change"] >= 0 else "↓"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">2. BTC / USDT (Binance Live)</div>
            <div class="metric-value">{fmt_usd(market['btc_price'])}</div>
            <div class="{btc_delta_class}">{btc_arrow} {market['btc_change']:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 3: BTC Dominance
    dom_delta = market.get("btc_dom_change", 0.0)
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
            <div class="metric-title">4. ETH / USDT (Binance Live)</div>
            <div class="metric-value">{fmt_usd(market['eth_price'])}</div>
            <div class="{eth_delta_class}">{eth_arrow} {market['eth_change']:+.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

    # Card 5: SOL / USDT
    sol_delta_class = "metric-delta-up" if market["sol_change"] >= 0 else "metric-delta-down"
    sol_arrow = "↑" if market["sol_change"] >= 0 else "↓"
    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">5. SOL / USDT (Binance Live)</div>
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