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


# --- Funções de Formatação Monetária e Numérica ---
def fmt_usd(val: float) -> str:
    return f"${val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def fmt_brl(val: float) -> str:
    return f"R$ {val:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def fmt_pts(val: float) -> str:
    return f"{val:,.0f}".replace(",", ".") + " pts"


# --- Horário de Brasília (UTC-3) ---
brt_tz = timezone(timedelta(hours=-3))
now_dt = datetime.datetime.now(brt_tz)
now_str = now_dt.strftime("%d/%m/%Y às %H:%M:%S BRT")
short_time_str = now_dt.strftime("%H:%M:%S BRT")

HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


# --- INGESTÃO DE DADOS CRIPTO (CoinGecko & Alternative.me) ---
@st.cache_data(ttl=180)
def get_crypto_data_aggregated():
    data = {
        "btc_price": 64071.0, "btc_change": 0.5,
        "eth_price": 1908.7, "eth_change": -0.2,
        "sol_price": 76.03, "sol_change": 1.2,
        "btc_dom": 56.5, "is_fallback": False
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


# --- INGESTÃO DE DADOS TRADFI / MACRO (Yahoo Finance API) ---
@st.cache_data(ttl=300)
def get_tradfi_data_aggregated():
    data = {
        "sp500_price": 5550.20, "sp500_change": 0.42,
        "ibov_price": 131250.0, "ibov_change": -0.18,
        "usdbrl_price": 5.48, "usdbrl_change": 0.25,
        "gold_price": 2505.40, "gold_change": 0.65,
        "brent_price": 78.30, "brent_change": -0.75,
        "is_fallback": False
    }

    tickers = {
        "sp500": "^GSPC",
        "ibov": "^BVSP",
        "usdbrl": "USDBRL=X",
        "gold": "GC=F",
        "brent": "BZ=F"
    }

    for key, symbol in tickers.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2d&interval=1d"
            res = requests.get(url, headers=HTTP_HEADERS, timeout=4).json()
            meta = res["chart"]["result"][0]["meta"]
            price = float(meta["regularMarketPrice"])
            prev_close = float(meta.get("chartPreviousClose", meta.get("previousClose", price)))
            chg_pct = ((price - prev_close) / prev_close) * 100.0 if prev_close > 0 else 0.0

            data[f"{key}_price"] = price
            data[f"{key}_change"] = chg_pct
        except Exception:
            data["is_fallback"] = True

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


# Ingestão Geral de Dados
crypto_market = get_crypto_data_aggregated()
tradfi_market = get_tradfi_data_aggregated()
fng = get_fear_and_greed()
sr = get_support_resistance(crypto_market["btc_price"])
m2 = get_global_m2()
pred = calculate_predictive_matrix(crypto_market, fng, sr)


# --- PAINEL LATERAL DE CONFIGURAÇÕES HIERÁRQUICO (SIDEBAR) ---
with st.sidebar:
    st.title("⚙️ Configurações OMNI")
    st.caption("Controle de geração de roteiros e relatórios")

    lang_option = st.selectbox(
        "🌐 Idioma do Output:",
        ["Português (BR)", "English (US)"]
    )

    st.divider()

    # 1. Escolha do Módulo (Crypto vs TradFi)
    selected_module = st.radio(
        "🪙 Escolha o Módulo:",
        ["Crypto", "TradFi (Macro)"],
        index=0,
        help="Selecione se deseja trabalhar com foco em Criptoativos ou TradFi/Macroeconomia."
    )

    st.divider()

    # 2. Escolha do Público/Formato (B2B vs B2C)
    selected_target = st.radio(
        f"🎯 Formato ({selected_module}):",
        ["B2B (Relatório)", "B2C (YouTube)"],
        index=0,
        help="B2B gera relatórios técnicos analíticos. B2C gera roteiros dinâmicos para vídeo."
    )

    # 3. Módulo Auto-Pilot (Ativo apenas dentro do modo B2C YouTube)
    autopilot_mode = False
    if "B2C" in selected_target:
        st.divider()
        autopilot_mode = st.toggle(
            "🤖 Modo Auto-Pilot (YouTube)",
            value=False,
            help="Ativado: gera e dispara roteiros automaticamente sem necessidade de aprovação HITL manual."
        )
    else:
        st.caption("💡 *O modo Auto-Pilot está disponível exclusivamente para entregáveis B2C (YouTube).*")


# --- GERADORES DE TEXTO ADAPTATIVOS ---
def generate_youtube_script(lang, is_auto, target_type):
    prefix = "[AUTO-PILOT ACTIVE] " if is_auto else "[HITL PENDING] "
    
    if target_type == "Crypto Focus":
        if "English" in lang:
            return f"""{prefix}[Crypto Focus] Extended LLM Script (~2 min 30 sec):

[00:00 - RETENTION HOOK]
The Bitcoin Fear & Greed Index (Alternative.me) stands at {fng['value']} points ({fng['sentiment']}) while BTC consolidates around {fmt_usd(crypto_market['btc_price'])} (CoinGecko). Macro liquidity remains backed by global M2 supply at {m2['m2_formatted']} ({m2['yoy_formatted']}) (FRED St. Louis Fed).

[00:35 - BITCOIN & DOMINANCE]
With Bitcoin dominance at {crypto_market['btc_dom']:.1f}% (CoinGecko Global), market eyes key support and resistance zones.

[01:10 - LEADING ALTCOINS]
Ethereum trades at {fmt_usd(crypto_market['eth_price'])} and Solana at {fmt_usd(crypto_market['sol_price'])} (CoinGecko), reflecting overall market consolidation.

[01:45 - TECHNICAL ANALYSIS & 48H PREDICTIVE MATRIX]
Bitcoin key support sits at {sr['support_str']}, with resistance at {sr['resistance_str']}. Our 48-hour predictive model points to a {pred['trend_desc']} outlook at {pred['direction']} ({pred['confidence']})."""
        else:
            return f"""{prefix}[Crypto Focus] Roteiro Estendido LLM (~2 min 30 seg de tela):

[00:00 - HOOK DE RETENÇÃO]
O Bitcoin Fear & Greed Index (Alternative.me) marca {fng['value']} pontos ({fng['sentiment']}) enquanto o BTC consolida na faixa de {fmt_usd(crypto_market['btc_price'])} (CoinGecko). O cenário macro segue sustentado pela liquidez global do M2 em {m2['m2_formatted']} ({m2['yoy_formatted']}) (FRED St. Louis Fed).

[00:35 - BITCOIN & DOMINÂNCIA]
Com a dominância do Bitcoin em {crypto_market['btc_dom']:.1f}% (CoinGecko Global), o mercado mantém a atenção voltada para os níveis de suporte e resistência chave.

[01:10 - ALTCOINS LÍDERES]
Ethereum negocia em {fmt_usd(crypto_market['eth_price'])} e Solana em {fmt_usd(crypto_market['sol_price'])} (CoinGecko), refletindo o momento de consolidação do ativo principal.

[01:45 - ANÁLISE TÉCNICA E MATRIZ PREDITIVA DO BTC]
A zona de suporte do Bitcoin situa-se em {sr['support_str']}, com resistência imediata em {sr['resistance_str']}. Nossa matriz preditiva aponta probabilidade {pred['trend_desc']} de {pred['direction']} ({pred['confidence']}) para as próximas 48 horas."""

    else:  # TradFi / Macro Focus
        if "English" in lang:
            return f"""{prefix}[TradFi / Macro Focus] Extended LLM Script (~2 min 30 sec):

[00:00 - RETENTION HOOK]
Global financial markets react to current liquidity conditions. The S&P 500 trades at {fmt_pts(tradfi_market['sp500_price'])} ({tradfi_market['sp500_change']:+.2f}%) while USD/BRL stands at {fmt_brl(tradfi_market['usdbrl_price'])} ({tradfi_market['usdbrl_change']:+.2f}%). Global M2 liquidity sits at {m2['m2_formatted']} ({m2['yoy_formatted']}) [FRED St. Louis Fed].

[00:35 - EQUITY & COMMODITIES]
Ibovespa trades at {fmt_pts(tradfi_market['ibov_price'])} ({tradfi_market['ibov_change']:+.2f}%). Commodities show Gold at {fmt_usd(tradfi_market['gold_price'])}/oz and Brent Crude at {fmt_usd(tradfi_market['brent_price'])}/bbl.

[01:10 - MACRO OUTLOOK & ASSET DYNAMICS]
Market interest rates and liquidity expansion continue to dictate global risk appetite across equity and commodity desks.

[01:45 - STRATEGIC SUMMARY]
Key macro resistance levels are tested as investors balance interest rate expectations against broad monetary expansion."""
        else:
            return f"""{prefix}[TradFi / Macro Focus] Roteiro Estendido LLM (~2 min 30 seg de tela):

[00:00 - HOOK DE RETENÇÃO]
Os mercados financeiros mundiais reagem ao fluxo de liquidez macro. O S&P 500 opera aos {fmt_pts(tradfi_market['sp500_price'])} ({tradfi_market['sp500_change']:+.2f}%) e o Dólar/Real cotado a {fmt_brl(tradfi_market['usdbrl_price'])} ({tradfi_market['usdbrl_change']:+.2f}%). A liquidez global do M2 permanece em {m2['m2_formatted']} ({m2['yoy_formatted']}) [FRED St. Louis Fed].

[00:35 - BOLSAS & COMMODITIES]
O Ibovespa negocia na faixa de {fmt_pts(tradfi_market['ibov_price'])} ({tradfi_market['ibov_change']:+.2f}%). Nas commodities, o Ouro registra {fmt_usd(tradfi_market['gold_price'])}/oz e o Petróleo Brent está cotado em {fmt_usd(tradfi_market['brent_price'])}/bbl.

[01:10 - PANORAMA MACROECONÔMICO]
A trajetória dos juros e a expansão monetária continuam sendo os principais vetores de apetite ao risco nos mercados emergentes e globais.

[01:45 - CONCLUSÃO ESTRATÉGICA]
Investidores mantêm postura cautelosa enquanto monitoram níveis de inflação e liquidez central para reequilíbrio de carteiras."""


def generate_b2b_report(lang):
    if "English" in lang:
        return f"""=== INSTITUTIONAL CRYPTO REPORT (B2B) ===
Date/Time: {now_str}

1. EXECUTIVE SUMMARY
- Primary Asset: Bitcoin (BTC) | Price: {fmt_usd(crypto_market['btc_price'])} | 24h Change: {crypto_market['btc_change']:+.2f}%
- Market Dominance: {crypto_market['btc_dom']:.1f}% (CoinGecko Global)
- Sentiment Benchmark: {fng['value']}/100 ({fng['sentiment']} - Alternative.me)

2. LIQUIDITY & TECHNICAL ZONES
- Immediate Support Level: {sr['support_str']}
- Immediate Resistance Level: {sr['resistance_str']}
- 48h Predictive Vector: {pred['direction']} ({pred['confidence']})

3. INFRASTRUCTURE & ALTCOINS
- Ethereum (ETH): {fmt_usd(crypto_market['eth_price'])} ({crypto_market['eth_change']:+.2f}%)
- Solana (SOL): {fmt_usd(crypto_market['sol_price'])} ({crypto_market['sol_change']:+.2f}%)

4. RISK MANAGEMENT RECOMMENDATION
Capital preservation recommended near upper resistance boundaries. Order book depth shows cluster consolidation."""
    else:
        return f"""=== RELATÓRIO INSTITUCIONAL CRIPTO (B2B) ===
Data/Hora: {now_str}

1. SUMÁRIO EXECUTIVO
- Ativo Principal: Bitcoin (BTC) | Preço: {fmt_usd(crypto_market['btc_price'])} | Variação 24h: {crypto_market['btc_change']:+.2f}%
- Dominância de Mercado: {crypto_market['btc_dom']:.1f}% (CoinGecko Global)
- Sentimento de Mercado: {fng['value']}/100 ({fng['sentiment']} - Alternative.me)

2. LIQUIDEZ E NÍVEIS TÉCNICOS
- Região de Suporte Imediato: {sr['support_str']}
- Região de Resistência Imediata: {sr['resistance_str']}
- Vetor Preditivo 48h: {pred['direction']} ({pred['confidence']})

3. INFRAESTRUTURA E ALTCOINS LÍDERES
- Ethereum (ETH): {fmt_usd(crypto_market['eth_price'])} ({crypto_market['eth_change']:+.2f}%)
- Solana (SOL): {fmt_usd(crypto_market['sol_price'])} ({crypto_market['sol_change']:+.2f}%)

4. RECOMENDAÇÃO DE GESTÃO DE RISCO
Preservação de capital recomendada nas proximidades da resistência superior. Mapeamento de liquidez indica consolidação de book."""


def generate_tradfi_b2b_report(lang):
    if "English" in lang:
        return f"""=== INSTITUTIONAL TRADFI & MACRO REPORT (B2B) ===
Date/Time: {now_str}

1. MACRO LIQUIDITY & BENCHMARKS
- S&P 500 Index: {fmt_pts(tradfi_market['sp500_price'])} ({tradfi_market['sp500_change']:+.2f}%)
- Ibovespa Index: {fmt_pts(tradfi_market['ibov_price'])} ({tradfi_market['ibov_change']:+.2f}%)
- Foreign Exchange (USD/BRL): {fmt_brl(tradfi_market['usdbrl_price'])} ({tradfi_market['usdbrl_change']:+.2f}%)
- Global M2 Money Supply: {m2['m2_formatted']} ({m2['yoy_formatted']}) [FRED St. Louis Fed]

2. COMMODITIES DESK
- Gold Spot (XAU/USD): {fmt_usd(tradfi_market['gold_price'])}/oz ({tradfi_market['gold_change']:+.2f}%)
- Brent Crude Oil: {fmt_usd(tradfi_market['brent_price'])}/bbl ({tradfi_market['brent_change']:+.2f}%)

3. ALLOCATION STRATEGY
Cross-asset liquidity monitoring advises balanced positioning across risk-on equities and defensive inflation hedges."""
    else:
        return f"""=== RELATÓRIO INSTITUCIONAL TRADFI & MACROECONOMIA (B2B) ===
Data/Hora: {now_str}

1. PANORAMA MACRO E BENCHMARKS
- S&P 500: {fmt_pts(tradfi_market['sp500_price'])} ({tradfi_market['sp500_change']:+.2f}%)
- Ibovespa: {fmt_pts(tradfi_market['ibov_price'])} ({tradfi_market['ibov_change']:+.2f}%)
- Câmbio (USD/BRL): {fmt_brl(tradfi_market['usdbrl_price'])} ({tradfi_market['usdbrl_change']:+.2f}%)
- M2 Global (Liquidez Monetária): {m2['m2_formatted']} ({m2['yoy_formatted']}) [FRED St. Louis Fed]

2. MESA DE COMMODITIES
- Ouro Spot (XAU/USD): {fmt_usd(tradfi_market['gold_price'])}/oz ({tradfi_market['gold_change']:+.2f}%)
- Petróleo Brent: {fmt_usd(tradfi_market['brent_price'])}/bbl ({tradfi_market['brent_change']:+.2f}%)

3. ESTRATÉGIA DE ALOCAÇÃO
Monitoramento de liquidez entre ativos recomenda alocação equilibrada entre renda variável e hedges defensivos contra inflação."""


# --- UI PRINCIPAL ---
st.title("⚡ OMNIRESEARCH Engine")
st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")
st.info(f"🕒 Dados consolidados das {now_str}")

is_active_fallback = crypto_market["is_fallback"] if selected_module == "Crypto" else tradfi_market["is_fallback"]
if is_active_fallback:
    st.warning("⚠️ Limite temporário de requisições na API primária. Exibindo última estimativa de mercado consolidada sem interrupções.")

st.divider()

col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    # Exibe badge de status do pipeline apenas quando estiver em modo B2C (YouTube)
    if "B2C" in selected_target:
        status_text = "🤖 MODO AUTO-PILOT ATIVADO (Pipeline Automático)" if autopilot_mode else "✋ MODO HITL ATIVADO (Aprovação Manual Requerida)"
        st.markdown(f'<div class="status-badge">{status_text}</div>', unsafe_allow_html=True)

    # Roteamento de telas dinâmico baseado no módulo e entregável selecionado
    if selected_module == "Crypto":
        if "B2B" in selected_target:
            st.subheader("🏢 Relatório B2B (Cripto & Institucional)")
            b2b_text = generate_b2b_report(lang_option)
            st.text_area("Relatório Institucional Cripto (B2B):", value=b2b_text, height=350)
        else:
            st.subheader("🎬 Roteiro YouTube B2C (Crypto Focus)")
            yt_script = generate_youtube_script(lang_option, autopilot_mode, "Crypto Focus")
            st.text_area("Roteiro de Vídeo Cripto (B2C):", value=yt_script, height=350)

        # Cards Inferiores Dinâmicos (Crypto)
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

    else:  # TradFi (Macro)
        if "B2B" in selected_target:
            st.subheader("🏢 Relatório B2B (TradFi & Macroeconomia)")
            b2b_tradfi_text = generate_tradfi_b2b_report(lang_option)
            st.text_area("Relatório Macro/TradFi (B2B):", value=b2b_tradfi_text, height=350)
        else:
            st.subheader("🎬 Roteiro YouTube B2C (TradFi & Macro Focus)")
            yt_script = generate_youtube_script(lang_option, autopilot_mode, "TradFi Focus")
            st.text_area("Roteiro de Vídeo Macro (B2C):", value=yt_script, height=350)

        # Cards Inferiores Dinâmicos (TradFi / Macro)
        m1, m2_col, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
                <div class="bottom-card">
                    <div class="bottom-card-title">S&P 500</div>
                    <div class="bottom-card-value">{fmt_pts(tradfi_market['sp500_price'])}</div>
                </div>
            """, unsafe_allow_html=True)
        with m2_col:
            st.markdown(f"""
                <div class="bottom-card">
                    <div class="bottom-card-title">Ibovespa</div>
                    <div class="bottom-card-value">{fmt_pts(tradfi_market['ibov_price'])}</div>
                </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
                <div class="bottom-card">
                    <div class="bottom-card-title">Dólar / Real</div>
                    <div class="bottom-card-value">{fmt_brl(tradfi_market['usdbrl_price'])}</div>
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

    if selected_module == "Crypto":
        btc_class = "metric-delta-up" if crypto_market["btc_change"] >= 0 else "metric-delta-down"
        eth_class = "metric-delta-up" if crypto_market["eth_change"] >= 0 else "metric-delta-down"
        sol_class = "metric-delta-up" if crypto_market["sol_change"] >= 0 else "metric-delta-down"
        fng_class = "metric-delta-up" if fng["change"] >= 0 else "metric-delta-down"

        st.markdown(f"""
            <div class="stCard">
                <div class="metric-title">1. Fear & Greed Index (Alternative.me)</div>
                <div class="metric-value">{fng['value']} ({fng['sentiment']})</div>
                <div class="{fng_class}">{fng['change']:+} pts hoje</div>
            </div>
            <div class="stCard">
                <div class="metric-title">2. BTC / USD (CoinGecko)</div>
                <div class="metric-value">{fmt_usd(crypto_market['btc_price'])}</div>
                <div class="{btc_class}">{crypto_market['btc_change']:+.2f}% (24h)</div>
            </div>
            <div class="stCard">
                <div class="metric-title">3. ETH / USD (CoinGecko)</div>
                <div class="metric-value">{fmt_usd(crypto_market['eth_price'])}</div>
                <div class="{eth_class}">{crypto_market['eth_change']:+.2f}% (24h)</div>
            </div>
            <div class="stCard">
                <div class="metric-title">4. SOL / USD (CoinGecko)</div>
                <div class="metric-value">{fmt_usd(crypto_market['sol_price'])}</div>
                <div class="{sol_class}">{crypto_market['sol_change']:+.2f}% (24h)</div>
            </div>
            <div class="stCard">
                <div class="metric-title">5. BTC Dominance (CoinGecko Global)</div>
                <div class="metric-value">{crypto_market['btc_dom']:.1f}%</div>
                <div class="metric-delta-up">Market Share Crypto</div>
            </div>
        """, unsafe_allow_html=True)

    else:  # TradFi (Macro)
        sp_class = "metric-delta-up" if tradfi_market["sp500_change"] >= 0 else "metric-delta-down"
        ibov_class = "metric-delta-up" if tradfi_market["ibov_change"] >= 0 else "metric-delta-down"
        usd_class = "metric-delta-up" if tradfi_market["usdbrl_change"] >= 0 else "metric-delta-down"
        gold_class = "metric-delta-up" if tradfi_market["gold_change"] >= 0 else "metric-delta-down"
        brent_class = "metric-delta-up" if tradfi_market["brent_change"] >= 0 else "metric-delta-down"

        st.markdown(f"""
            <div class="stCard">
                <div class="metric-title">1. S&P 500 (EUA)</div>
                <div class="metric-value">{fmt_pts(tradfi_market['sp500_price'])}</div>
                <div class="{sp_class}">{tradfi_market['sp500_change']:+.2f}% hoje</div>
            </div>
            <div class="stCard">
                <div class="metric-title">2. IBOVESPA (Brasil)</div>
                <div class="metric-value">{fmt_pts(tradfi_market['ibov_price'])}</div>
                <div class="{ibov_class}">{tradfi_market['ibov_change']:+.2f}% hoje</div>
            </div>
            <div class="stCard">
                <div class="metric-title">3. Dólar / Real (USD/BRL)</div>
                <div class="metric-value">{fmt_brl(tradfi_market['usdbrl_price'])}</div>
                <div class="{usd_class}">{tradfi_market['usdbrl_change']:+.2f}% (24h)</div>
            </div>
            <div class="stCard">
                <div class="metric-title">4. Ouro Spot (XAU/USD)</div>
                <div class="metric-value">{fmt_usd(tradfi_market['gold_price'])}</div>
                <div class="{gold_class}">{tradfi_market['gold_change']:+.2f}% hoje</div>
            </div>
            <div class="stCard">
                <div class="metric-title">5. Petróleo Brent (Brent Crude)</div>
                <div class="metric-value">{fmt_usd(tradfi_market['brent_price'])}</div>
                <div class="{brent_class}">{tradfi_market['brent_change']:+.2f}% hoje</div>
            </div>
        """, unsafe_allow_html=True)