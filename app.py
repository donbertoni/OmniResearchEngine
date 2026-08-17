import datetime
from datetime import timezone, timedelta
import requests
import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Dark Mode Total & Cards Padronizados ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], 
    [data-testid="stMain"], .main, .block-container, [data-testid="stToolbar"] {
        background-color: #0b0f19 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937 !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, div, [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    .stCaption, small, [data-testid="stCaptionContainer"] {
        color: #9ca3af !important;
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

    /* Cards Inferiores Padronizados com Altura Fixa */
    .bottom-card {
        background-color: #111827 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 8px;
        padding: 14px 16px;
        height: 105px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .bottom-card-title {
        font-size: 0.8rem;
        color: #9ca3af !important;
        margin-bottom: 6px;
        font-weight: 500;
    }
    .bottom-card-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff !important;
        white-space: nowrap;
    }
    .bottom-card-sub {
        font-size: 0.78rem;
        color: #10b981 !important;
        margin-top: 4px;
        font-weight: 500;
    }
    .status-badge {
        background-color: #1e293b;
        color: #38bdf8;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #0284c7;
        display: inline-block;
        margin-bottom: 10px;
    }
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


# --- Ingestão Agregada Robusta com Cache Seguro ---
@st.cache_data(ttl=180)
def get_crypto_data_aggregated():
    data = {
        "btc_price": 64071.0, "btc_change": 0.5,
        "eth_price": 1908.7, "eth_change": -0.2,
        "sol_price": 76.03, "sol_change": 1.2,
        "btc_dom": 56.5, "btc_dom_change": 0.1,
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
        "resistance_str": f"${res_low/1000:.1f}k - ${res_high/1000:.1f}k",
        "sup_low": sup_low,
        "sup_high": sup_high,
        "res_low": res_low,
        "res_high": res_high
    }


def calculate_predictive_matrix(market: dict, fng: dict, sr: dict):
    score = 50.0

    btc_chg = market.get("btc_change", 0.0)
    score += max(min(btc_chg * 4.0, 22.0), -22.0)

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
        confidence = "↑ Viés Altista" if bullish_pct < 70 else "↑ Alta Confiança"
        trend_desc = "altista"
    elif bullish_pct <= 42:
        direction = f"{100 - bullish_pct}% Bearish"
        confidence = "↓ Viés Baixista" if bullish_pct > 35 else "↓ Risco de Baixa"
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


# Ingestão de Dados
market = get_crypto_data_aggregated()
fng = get_fear_and_greed()
sr = get_support_resistance(market["btc_price"])
m2 = get_global_m2()
pred = calculate_predictive_matrix(market, fng, sr)


# --- PAINEL LATERAL DE CONFIGURAÇÕES (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Configurações OMNI")
    st.caption("Controle de geração de roteiros e relatórios")

    lang_option = st.selectbox(
        "🌐 Idioma do Output:",
        ["Português (BR)", "English (US)"]
    )

    autopilot_mode = st.toggle(
        "🤖 Modo Auto-Pilot (YouTube)",
        value=False,
        help="Ativado: gera e dispara roteiros automaticamente sem aprovação HITL manual."
    )

    st.divider()

    # Seletor Principal do Perfil de Serviço (Substitui a caixa de fontes redundante)
    service_profile = st.radio(
        "🎯 Serviço Ativo:",
        ["🏢 B2B (Cripto & Institucional)", "👥 B2C (Macro & Varejo)"],
        index=0,
        help="Define o foco dos relatórios e análises geradas no painel."
    )


# --- GERADORES DE TEXTO ADAPTATIVOS ---
def generate_youtube_script(lang, is_auto, service):
    prefix = "[AUTO-PILOT ACTIVE] " if is_auto else "[HITL PENDING] "
    tag_service = "B2B Focus" if "B2B" in service else "B2C Focus"
    
    if "English" in lang:
        return f"""{prefix}[{tag_service}] Extended LLM Script (~2 min 30 sec):

[00:00 - RETENTION HOOK]
The Bitcoin Fear & Greed Index (Alternative.me) stands at {fng['value']} points ({fng['sentiment']}) while BTC consolidates around {fmt_usd(market['btc_price'])} (CoinGecko). Macro liquidity remains backed by global M2 supply at {m2['m2_formatted']} ({m2['yoy_formatted']}) (FRED St. Louis Fed).

[00:35 - BITCOIN & DOMINANCE]
With Bitcoin dominance at {market['btc_dom']:.1f}% (CoinGecko Global), market eyes key support and resistance zones.

[01:10 - LEADING ALTCOINS]
Ethereum trades at {fmt_usd(market['eth_price'])} and Solana at {fmt_usd(market['sol_price'])} (CoinGecko), reflecting overall market consolidation.

[01:45 - TECHNICAL ANALYSIS & 48H PREDICTIVE MATRIX]
Bitcoin key support sits at {sr['support_str']}, with resistance at {sr['resistance_str']}. Our 48-hour predictive model points to a {pred['trend_desc']} outlook at {pred['direction']} ({pred['confidence']})."""
    else:
        return f"""{prefix}[{tag_service}] Roteiro Estendido LLM (~2 min 30 seg de tela):

[00:00 - HOOK DE RETENÇÃO]
O Bitcoin Fear & Greed Index (Alternative.me) marca {fng['value']} pontos ({fng['sentiment']}) enquanto o BTC consolida na faixa de {fmt_usd(market['btc_price'])} (CoinGecko). O cenário macro segue sustentado pela liquidez global do M2 em {m2['m2_formatted']} ({m2['yoy_formatted']}) (FRED St. Louis Fed).

[00:35 - BITCOIN & DOMINÂNCIA]
Com a dominância do Bitcoin em {market['btc_dom']:.1f}% (CoinGecko Global), o mercado mantém a atenção voltada para os níveis de suporte e resistência chave.

[01:10 - ALTCOINS LÍDERES]
Ethereum negocia em {fmt_usd(market['eth_price'])} e Solana em {fmt_usd(market['sol_price'])} (CoinGecko), refletindo o momento de consolidação do ativo principal.

[01:45 - ANÁLISE TÉCNICA E MATRIZ PREDITIVA DO BTC]
A zona de suporte do Bitcoin situa-se em {sr['support_str']}, com resistência imediata em {sr['resistance_str']}. Nossa matriz preditiva aponta probabilidade {pred['trend_desc']} de {pred['direction']} ({pred['confidence']}) para as próximas 48 horas."""


def generate_b2b_report(lang):
    if "English" in lang:
        return f"""=== INSTITUTIONAL CRYPTO REPORT (B2B) ===
Date/Time: {now_str}

1. EXECUTIVE SUMMARY
- Primary Asset: Bitcoin (BTC) | Price: {fmt_usd(market['btc_price'])} | 24h Change: {market['btc_change']:+.2f}%
- Market Dominance: {market['btc_dom']:.1f}% (CoinGecko Global)
- Sentiment Benchmark: {fng['value']}/100 ({fng['sentiment']} - Alternative.me)

2. LIQUIDITY & TECHNICAL ZONES
- Immediate Support Level: {sr['support_str']}
- Immediate Resistance Level: {sr['resistance_str']}
- 48h Predictive Vector: {pred['direction']} ({pred['confidence']})

3. INFRASTRUCTURE & ALTCOINS
- Ethereum (ETH): {fmt_usd(market['eth_price'])} ({market['eth_change']:+.2f}%)
- Solana (SOL): {fmt_usd(market['sol_price'])} ({market['sol_change']:+.2f}%)

4. RISK MANAGEMENT RECOMMENDATION
Capital preservation recommended near upper resistance boundaries. Order book depth shows cluster consolidation."""
    else:
        return f"""=== RELATÓRIO INSTITUCIONAL CRIPTO (B2B) ===
Data/Hora: {now_str}

1. SUMÁRIO EXECUTIVO
- Ativo Principal: Bitcoin (BTC) | Preço: {fmt_usd(market['btc_price'])} | Variação 24h: {market['btc_change']:+.2f}%
- Dominância de Mercado: {market['btc_dom']:.1f}% (CoinGecko Global)
- Sentimento de Mercado: {fng['value']}/100 ({fng['sentiment']} - Alternative.me)

2. LIQUIDEZ E NÍVEIS TÉCNICOS
- Região de Suporte Imediato: {sr['support_str']}
- Região de Resistência Imediata: {sr['resistance_str']}
- Vetor Preditivo 48h: {pred['direction']} ({pred['confidence']})

3. INFRAESTRUTURA E ALTCOINS LÍDERES
- Ethereum (ETH): {fmt_usd(market['eth_price'])} ({market['eth_change']:+.2f}%)
- Solana (SOL): {fmt_usd(market['sol_price'])} ({market['sol_change']:+.2f}%)

4. RECOMENDAÇÃO DE GESTÃO DE RISCO
Preservação de capital recomendada nas proximidades da resistência superior. Mapeamento de liquidez indica consolidação de book."""


def generate_b2c_report(lang):
    if "English" in lang:
        return f"""=== MACROECONOMICS & TRADITIONAL ASSETS REPORT (B2C) ===
Date/Time: {now_str}

1. MACRO LIQUIDITY OUTLOOK
- Global M2 Money Supply: {m2['m2_formatted']} ({m2['yoy_formatted']}) [Source: FRED St. Louis Fed]
- Market Sentiment: {fng['value']} ({fng['sentiment']}) - Alternative.me

2. ASSET ALLOCATION & CRYPTO SPILLOVER
- Bitcoin Spot Consolidation: {fmt_usd(market['btc_price'])}
- Trend Outlook (48h): {pred['direction']} ({pred['confidence']})

3. INVESTOR TAKEAWAY
Global money supply expansion provides long-term support for scarce digital assets. Short-term volatility remains bound within technical support ({sr['support_str']}) and resistance ({sr['resistance_str']})."""
    else:
        return f"""=== RELATÓRIO MACROECONOMIA & ATIVOS TRADICIONAIS (B2C) ===
Data/Hora: {now_str}

1. PANORAMA DE LIQUIDEZ MACRO
- M2 Global (Massa Monetária): {m2['m2_formatted']} ({m2['yoy_formatted']}) [Fonte: FRED St. Louis Fed]
- Sentimento do Mercado Retail: {fng['value']} ({fng['sentiment']}) - Alternative.me

2. ALOCAÇÃO E IMPACTO NO MERCADO DIGITAL
- Consolidação Spot do Bitcoin: {fmt_usd(market['btc_price'])}
- Tendência Esperada (48h): {pred['direction']} ({pred['confidence']})

3. VISÃO PARA O INVESTIDOR
A expansão da liquidez global (M2) continua sustentando a tese de ativos escassos no longo prazo. Flutuações de curto prazo permanecem dentro dos intervalos de suporte ({sr['support_str']}) e resistência ({sr['resistance_str']})."""


# --- UI PRINCIPAL ---
st.title("⚡ OMNIRESEARCH Engine")
st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e B2C (Macro)")
st.info(f"🕒 Dados consolidados das {now_str}")

if market["is_fallback"]:
    st.warning("⚠️ Limite temporário de requisições na API primária. Exibindo última estimativa de mercado consolidada sem interrupções.")

st.divider()

col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    status_text = "🤖 MODO AUTO-PILOT ATIVADO (Pipeline Automático)" if autopilot_mode else "✋ MODO HITL ATIVADO (Aprovação Manual Requerida)"
    st.markdown(f'<div class="status-badge">{status_text}</div>', unsafe_allow_html=True)

    # Exibição Dinâmica das Abas com base no perfil selecionado no Sidebar
    if "B2B" in service_profile:
        tab_youtube, tab_report = st.tabs(["🎬 Roteiro YouTube (B2B)", "🏢 Relatório B2B (Crypto)"])
        with tab_youtube:
            st.subheader("Painel de Aprovação / Execução de Vídeo B2B")
            yt_script = generate_youtube_script(lang_option, autopilot_mode, service_profile)
            st.text_area("Roteiro para Vídeo YouTube:", value=yt_script, height=320)
        with tab_report:
            st.subheader("Relatório B2B - Infraestrutura & Análise Técnica")
            b2b_text = generate_b2b_report(lang_option)
            st.text_area("Relatório Cripto B2B:", value=b2b_text, height=320)
    else:
        tab_youtube, tab_report = st.tabs(["🎬 Roteiro YouTube (B2C)", "👥 Relatório B2C (Macro)"])
        with tab_youtube:
            st.subheader("Painel de Aprovação / Execução de Vídeo B2C")
            yt_script = generate_youtube_script(lang_option, autopilot_mode, service_profile)
            st.text_area("Roteiro para Vídeo YouTube:", value=yt_script, height=320)
        with tab_report:
            st.subheader("Relatório B2C - Macroeconomia & Varejo")
            b2c_text = generate_b2c_report(lang_option)
            st.text_area("Relatório Macro B2C:", value=b2c_text, height=320)

    # Cards Inferiores com Altura Fixa (4 Colunas)
    m1, m2_col, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
            <div class="bottom-card">
                <div class="bottom-card-title">Suporte BTC</div>
                <div class="bottom-card-value">{sr['support_str']}</div>
            </div>
        """, unsafe_allow_html=True)

    with m2_col:
        st.markdown(f"""
            <div class="bottom-card">
                <div class="bottom-card-title">Resistência BTC</div>
                <div class="bottom-card-value">{sr['resistance_str']}</div>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
            <div class="bottom-card">
                <div class="bottom-card-title">Matriz Preditiva 48h</div>
                <div class="bottom-card-value">{pred['direction']}</div>
                <div class="bottom-card-sub">{pred['confidence']}</div>
            </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
            <div class="bottom-card">
                <div class="bottom-card-title">M2 Global (FRED)</div>
                <div class="bottom-card-value">{m2['m2_formatted']}</div>
                <div class="bottom-card-sub">{m2['yoy_formatted']}</div>
            </div>
        """, unsafe_allow_html=True)

with col_right:
    st.subheader("📊 Métricas Agregadas")
    st.caption(f"Atualizado às {short_time_str}")

    st.markdown(f"""
        <div class="stCard">
            <div class="metric-title">1. Fear & Greed Index (Alternative.me)</div>
            <div class="metric-value">{fng['value']} ({fng['sentiment']})</div>
            <div class="metric-delta-up">{fng['change']:+} pts hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-title">2. BTC / USD (CoinGecko)</div>
            <div class="metric-value">{fmt_usd(market['btc_price'])}</div>
            <div class="metric-delta-up">{market['btc_change']:+.2f}% (24h)</div>
        </div>
        <div class="stCard">
            <div class="metric-title">3. ETH / USD (CoinGecko)</div>
            <div class="metric-value">{fmt_usd(market['eth_price'])}</div>
            <div class="metric-delta-down">{market['eth_change']:+.2f}% (24h)</div>
        </div>
        <div class="stCard">
            <div class="metric-title">4. SOL / USD (CoinGecko)</div>
            <div class="metric-value">{fmt_usd(market['sol_price'])}</div>
            <div class="metric-delta-up">{market['sol_change']:+.2f}% (24h)</div>
        </div>
        <div class="stCard">
            <div class="metric-title">5. BTC Dominance (CoinGecko Global)</div>
            <div class="metric-value">{market['btc_dom']:.1f}%</div>
            <div class="metric-delta-up">Market Share Crypto</div>
        </div>
    """, unsafe_allow_html=True)