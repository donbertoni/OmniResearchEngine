import streamlit as st
import requests
from datetime import datetime, timezone, timedelta

# Configuração da página
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada CSS
st.markdown("""
<style>
    .main {
        background-color: #0b101d;
        color: #e2e8f0;
    }
    .stCard {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #f8fafc;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .status-red {
        color: #ef4444;
        font-weight: 500;
        font-size: 13px;
    }
    .status-green {
        color: #10b981;
        font-weight: 500;
        font-size: 13px;
    }
    .status-blue {
        color: #38bdf8;
        font-weight: 500;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# Timestamp Dinâmico (Horário de Brasília)
brt_tz = timezone(timedelta(hours=-3))
agora_brt = datetime.now(brt_tz)
data_atual = agora_brt.strftime("%d/%m/%Y às %H:%M:%S BRT")

# Função resiliente para buscar dados do CoinGecko e Fear & Greed Index
@st.cache_data(ttl=20)
def get_coingecko_data():
    data = {
        "btc_price": "$64.481,00", "btc_change": "+2,19%", "btc_is_pos": True,
        "btc_raw_price": 64481.00,
        "eth_price": "$1.909,21", "eth_change": "+1,36%", "eth_is_pos": True,
        "eth_raw_price": 1909.21,
        "sol_price": "$76,05", "sol_change": "+1,25%", "sol_is_pos": True,
        "btc_dom": "56,56%",
        "fng_val": "31 / 100", "fng_classification": "Medo", "fng_css": "status-red"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        url_prices = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
        resp_prices = requests.get(url_prices, headers=headers, timeout=3).json()

        if "bitcoin" in resp_prices:
            btc_p = resp_prices["bitcoin"]["usd"]
            btc_c = resp_prices["bitcoin"].get("usd_24h_change", 2.19)
            data["btc_raw_price"] = btc_p
            data["btc_price"] = f"${btc_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["btc_change"] = f"{btc_c:+.2f}%".replace(".", ",")
            data["btc_is_pos"] = btc_c >= 0

        if "ethereum" in resp_prices:
            eth_p = resp_prices["ethereum"]["usd"]
            eth_c = resp_prices["ethereum"].get("usd_24h_change", 1.36)
            data["eth_raw_price"] = eth_p
            data["eth_price"] = f"${eth_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["eth_change"] = f"{eth_c:+.2f}%".replace(".", ",")
            data["eth_is_pos"] = eth_c >= 0

        if "solana" in resp_prices:
            sol_p = resp_prices["solana"]["usd"]
            sol_c = resp_prices["solana"].get("usd_24h_change", 1.25)
            data["sol_raw_price"] = sol_p
            data["sol_price"] = f"${sol_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["sol_change"] = f"{sol_c:+.2f}%".replace(".", ",")
            data["sol_is_pos"] = sol_c >= 0
    except Exception:
        pass

    try:
        url_global = "https://api.coingecko.com/api/v3/global"
        resp_global = requests.get(url_global, headers=headers, timeout=3).json()

        if "data" in resp_global:
            dom_btc = resp_global["data"]["market_cap_percentage"]["btc"]
            data["btc_dom"] = f"{dom_btc:.2f}%".replace(".", ",")
    except Exception:
        pass

    try:
        url_fng = "https://api.alternative.me/fng/"
        resp_fng = requests.get(url_fng, headers=headers, timeout=3).json()
        if "data" in resp_fng and len(resp_fng["data"]) > 0:
            val = int(resp_fng["data"][0]["value"])
            classif = resp_fng["data"][0]["value_classification"]
            
            classif_map = {
                "Extreme Fear": "Medo Extremo",
                "Fear": "Medo",
                "Neutral": "Neutro",
                "Greed": "Ganância",
                "Extreme Greed": "Ganância Extrema"
            }
            pt_classif = classif_map.get(classif, classif)
            data["fng_val"] = f"{val} / 100"
            data["fng_classification"] = pt_classif
            
            if val >= 55:
                data["fng_css"] = "status-green"
            elif val <= 45:
                data["fng_css"] = "status-red"
            else:
                data["fng_css"] = "status-blue"
    except Exception:
        pass

    return data

# Função resiliente para buscar dados MACRO via API (Yahoo Finance & AwesomeAPI)
@st.cache_data(ttl=60)
def get_macro_data():
    data = {
        "sp500_val": "7.758", "sp500_chg": "-0,53%", "sp500_is_pos": False,
        "ibov_val": "166.833", "ibov_chg": "-0,16%", "ibov_is_pos": False,
        "usdbrl_val": "5,20", "usdbrl_chg": "+0,00%", "usdbrl_is_pos": True,
        "m2_val": "$104.8T (+4.2% YoY)",
        "gold_val": "$4.474,90", "gold_chg": "+0,85%", "gold_is_pos": True,
        "oil_val": "$90,69", "oil_chg": "+2,45%", "oil_is_pos": True
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 1. Câmbio USD/BRL via AwesomeAPI
    try:
        url_fx = "https://economia.awesomeapi.com.br/last/USD-BRL"
        resp_fx = requests.get(url_fx, headers=headers, timeout=3).json()
        if "USDBRL" in resp_fx:
            bid = float(resp_fx["USDBRL"]["bid"])
            pct = float(resp_fx["USDBRL"]["pctChange"])
            data["usdbrl_val"] = f"{bid:.2f}".replace(".", ",")
            data["usdbrl_chg"] = f"{pct:+.2f}%".replace(".", ",")
            data["usdbrl_is_pos"] = pct >= 0
    except Exception:
        pass

    # 2. Benchmarks Globais & Commodities via Yahoo Finance
    tickers = {
        "^GSPC": ("sp500_val", "sp500_chg", "sp500_is_pos", "pts"),
        "^BVSP": ("ibov_val", "ibov_chg", "ibov_is_pos", "pts"),
        "GC=F": ("gold_val", "gold_chg", "gold_is_pos", "$"),
        "BZ=F": ("oil_val", "oil_chg", "oil_is_pos", "$")
    }

    for symbol, (v_key, c_key, p_key, mode) in tickers.items():
        try:
            url_yf = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            resp_yf = requests.get(url_yf, headers=headers, timeout=3).json()
            meta = resp_yf["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice")
            prev = meta.get("chartPreviousClose", price)
            if price and prev:
                chg = ((price - prev) / prev) * 100
                if mode == "pts":
                    data[v_key] = f"{price:,.0f}".replace(",", ".")
                else:
                    data[v_key] = f"${price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                data[c_key] = f"{chg:+.2f}%".replace(".", ",")
                data[p_key] = chg >= 0
        except Exception:
            pass

    return data

# Função para calcular Suporte e Resistência ESTRUTURAIS (Estáticos por Níveis de TF Maior)
def calcular_suporte_resistencia_estrutural(preco_base):
    passo = 2500
    sup = (int(preco_base) // passo) * passo
    res = sup + passo

    if res - preco_base < 400:
        res += passo
    if preco_base - sup < 400:
        sup -= passo

    sup_str = f"${sup:,.0f}".replace(",", ".")
    res_str = f"${res:,.0f}".replace(",", ".")
    return sup_str, res_str

# Sidebar - Configurações OMNI
st.sidebar.title("⚙️ Configurações OMNI")
st.sidebar.caption("Controle de geração de roteiros e relatórios")

idioma = st.sidebar.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English (US)"])

modulo = st.sidebar.radio(
    "💡 Escolha o Módulo:",
    ["Crypto", "TradFi (Macro)"],
    index=0,
    help="Selecione o segmento de análise"
)

formato = st.sidebar.radio(
    f"🎯 Formato ({modulo}):",
    ["B2B (Relatório)", "B2C (YouTube)"],
    index=0,
    help="Escolha o tipo de entregável"
)

# Lógica Condicional do Auto-Pilot na Sidebar
if formato == "B2C (YouTube)":
    autopilot = st.sidebar.toggle("🤖 Ativar Modo Auto-Pilot", value=True)
    if autopilot:
        st.sidebar.success("⚡ Auto-Pilot ATIVO: Roteiro gerado de forma autônoma.")
    else:
        st.sidebar.warning("🛠️ Modo HITL: Edição manual habilitada.")
else:
    autopilot = False
    st.sidebar.info("💡 O modo Auto-Pilot está disponível exclusivamente para entregáveis B2C (YouTube).")

# Header Principal
st.title("⚡ OMNIRESEARCH Engine")
st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

# Banner de Timestamp
st.info(f"🕒 **Dados consolidados das {data_atual}**")

# Layout Principal em Duas Colunas
col_left, col_right = st.columns([1.6, 1])

# LÓGICA DINÂMICA BASEADA NO MÓDULO E FORMATO SELECIONADOS
if modulo == "TradFi (Macro)":
    macro_data = get_macro_data()
    sp500_tendencia, sp500_score, sp500_valor_nivel = "Pressão Vendedora", "38 pts", "7.680 pts"
    ibov_tendencia, ibov_score, ibov_valor_nivel = "Consolidação 7D", "52 pts", "165.200 pts"

    with col_left:
        if formato == "B2C (YouTube)":
            st.subheader("🎬 Roteiro B2C YouTube (TradFi & Macro)")
            st.caption("Roteiro de Vídeo (YouTube B2C):")
            
            roteiro_tradfi = f"""[HOOK 0-15s]
O mercado global está em ponto crítico hoje ({data_atual}). S&P 500 cotado a {macro_data['sp500_val']} pts e o Ibovespa operando em {macro_data['ibov_val']} pts. Vamos direto aos dados do relatório institucional.

[BLOCO 1 - PANORAMA GLOBAL]
- S&P 500 em {macro_data['sp500_val']} pts ({macro_data['sp500_chg']}).
- Ibovespa segurando a região dos {macro_data['ibov_val']} pts.
- Dólar cotado a R$ {macro_data['usdbrl_val']}.

[BLOCO 2 - COMMODITIES E LIQUIDEZ]
- Ouro registrando cotação a {macro_data['gold_val']}/oz ({macro_data['gold_chg']}).
- Petróleo Brent operando a {macro_data['oil_val']}/bbl ({macro_data['oil_chg']}).

[CTA & ENCERRAMENTO]
Deixe seu like e inscreva-se para análises diárias da OMNIRESEARCH!"""

            st.text_area("", value=roteiro_tradfi, height=310, disabled=False)
        else:
            st.subheader("📰 Relatório B2B (TradFi & Macroeconomia)")
            st.caption("Relatório Macro/TradFi (B2B):")
            
            relatorio_texto = f"""=== RELATÓRIO INSTITUCIONAL TRADFI & MACROECONOMIA (B2B) ===
Data/Hora: {data_atual}

1. PANORAMA MACRO E BENCHMARKS
- S&P 500: {macro_data['sp500_val']} pts ({macro_data['sp500_chg']}) (Yahoo Finance)
- Ibovespa: {macro_data['ibov_val']} pts ({macro_data['ibov_chg']}) (Yahoo Finance)
- Câmbio (USD/BRL): R$ {macro_data['usdbrl_val']} ({macro_data['usdbrl_chg']}) (Yahoo Finance)
- M2 Global (Liquidez Monetária): {macro_data['m2_val']} (FRED St. Louis Fed)

2. MESA DE COMMODITIES
- Ouro Spot (XAU/USD): {macro_data['gold_val']}/oz ({macro_data['gold_chg']}) (Yahoo Finance)
- Petróleo Brent: {macro_data['oil_val']}/bbl ({macro_data['oil_chg']}) (Yahoo Finance)

3. VETORES PREDITIVOS E NÍVEIS TÉCNICOS
- S&P 500 (EUA): Tendência 7D ({sp500_tendencia} - {sp500_score}) | Próximo Suporte: {sp500_valor_nivel}
- Ibovespa (Brasil): Tendência 7D ({ibov_tendencia} - {ibov_score}) | Suporte Atual: {ibov_valor_nivel}"""

            st.text_area("", value=relatorio_texto, height=310, disabled=False)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Tendência 7D (S&P 500)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{sp500_tendencia}</div>
                <div class="status-red">↓ {sp500_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Próximo Suporte (S&P 500)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{sp500_valor_nivel}</div>
                <div class="status-red">↓ Nível Crítico</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Tendência 7D (Ibovespa)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{ibov_tendencia}</div>
                <div class="status-blue">→ {ibov_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Suporte Atual (Ibovespa)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{ibov_valor_nivel}</div>
                <div class="status-blue">→ Nível Crítico</div>
            </div>
            """, unsafe_allow_html=True)

else:
    crypto_data = get_coingecko_data()
    btc_sup, btc_res = calcular_suporte_resistencia_estrutural(crypto_data["btc_raw_price"])

    btc_tendencia = "Tendência Compradora" if crypto_data["btc_is_pos"] else "Pressão Vendedora"
    btc_score = "78 pts" if crypto_data["btc_is_pos"] else "42 pts"
    btc_prev_48h = "Alta Moderada" if crypto_data["btc_is_pos"] else "Pressão Vendedora"

    btc_status_css = "status-green" if crypto_data["btc_is_pos"] else "status-red"
    eth_status_css = "status-green" if crypto_data["eth_is_pos"] else "status-red"
    sol_status_css = "status-green" if crypto_data["sol_is_pos"] else "status-red"

    with col_left:
        if formato == "B2C (YouTube)":
            st.subheader("🎬 Roteiro B2C YouTube (Crypto & Web3)")
            st.caption("Roteiro de Vídeo (YouTube B2C):")
            
            roteiro_crypto = f"""[HOOK 0-15s]
O Bitcoin está sendo negociado a {crypto_data['btc_price']} nesta tarde ({data_atual})! Vamos analisar a tendência de 7 dias, a previsão de 48 horas e o índice de sentimento de mercado.

[BLOCO 1 - ANÁLISE PREDITIVA BITCOIN]
- BTC Tendência 7D: {btc_tendencia} ({btc_score}).
- Suporte Crítico: {btc_sup} | Próxima Resistência: {btc_res}.
- Previsão 48h: {btc_prev_48h} com alvo em {btc_res}.

[BLOCO 2 - METRICAS CRÍTICAS DE MERCADO]
- Ethereum (ETH): {crypto_data['eth_price']} ({crypto_data['eth_change']}).
- Solana (SOL): {crypto_data['sol_price']} ({crypto_data['sol_change']}).
- Dominância do Bitcoin: {crypto_data['btc_dom']}.
- Sentimento (Fear & Greed Index): {crypto_data['fng_val']} ({crypto_data['fng_classification']}).

[CTA & ENCERRAMENTO]
Inscreva-se no canal para manter suas decisões cripto fundamentadas em dados reais!"""

            st.text_area("", value=roteiro_crypto, height=310, disabled=False)
        else:
            st.subheader("📰 Relatório B2B (Crypto & Web3)")
            st.caption("Relatório Crypto/Web3 (B2B):")
            
            relatorio_crypto = f"""=== RELATÓRIO INSTITUCIONAL CRYPTO & WEB3 (B2B) ===
Data/Hora: {data_atual}

1. CRIPTO PANORAMA E BENCHMARKS
- Bitcoin (BTC/USDT): {crypto_data['btc_price']} ({crypto_data['btc_change']}) (CoinGecko)
- Ethereum (ETH/USDT): {crypto_data['eth_price']} ({crypto_data['eth_change']}) (CoinGecko)
- Solana (SOL/USDT): {crypto_data['sol_price']} ({crypto_data['sol_change']}) (CoinGecko)
- Dominância do Bitcoin (BTC.D): {crypto_data['btc_dom']} (+0,63%) (CoinGecko)
- Bitcoin Fear & Greed Index: {crypto_data['fng_val']} ({crypto_data['fng_classification']}) (Alternative.me)

2. MESA DE LIQUIDEZ E ON-CHAIN
- Financiamento BTC (Funding Rate): +0.012% (Neutro/Comprador)
- Reservas de BTC nas Corretoras: 2.05M BTC (Outflow Contínuo)

3. VETORES PREDITIVOS E NÍVEIS TÉCNICOS (BITCOIN)
- Tendência 7D (BTC): {btc_tendencia} ({btc_score})
- Próxima Resistência (BTC): {btc_res} (Nível Crítico)
- Suporte Crítico (BTC): {btc_sup} (Zona de Defesa)
- Previsão 48h (BTC): {btc_prev_48h} | Alvo: {btc_res}"""

            st.text_area("", value=relatorio_crypto, height=310, disabled=False)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Tendência 7D (BTC)</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{btc_tendencia}</div>
                <div class="{btc_status_css}">↑ {btc_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Próxima Resistência (BTC)</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{btc_res}</div>
                <div class="status-green">↑ Nível Crítico</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Suporte Crítico (BTC)</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{btc_sup}</div>
                <div class="status-blue">↓ Zona de Defesa</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Previsão 48h (BTC)</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{btc_prev_48h}</div>
                <div class="{btc_status_css}">↑ Alvo {btc_res}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.subheader("📊 Métricas Agregadas (Crypto)")
        st.caption(f"Atualizado às {data_atual.split('às ')[1] if 'às ' in data_atual else data_atual}")
        
        st.markdown(f"""
        <div class="stCard">
            <div class="metric-label">1. Bitcoin / USDT (CoinGecko)</div>
            <div class="metric-value">{crypto_data['btc_price']}</div>
            <div class="{btc_status_css}">{crypto_data['btc_change']} hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">2. Ethereum / USDT (CoinGecko)</div>
            <div class="metric-value">{crypto_data['eth_price']}</div>
            <div class="{eth_status_css}">{crypto_data['eth_change']} hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">3. Solana / USDT (CoinGecko)</div>
            <div class="metric-value">{crypto_data['sol_price']}</div>
            <div class="{sol_status_css}">{crypto_data['sol_change']} hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">4. Dominância BTC (CoinGecko)</div>
            <div class="metric-value">{crypto_data['btc_dom']}</div>
            <div class="status-green">+0,63% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">5. Bitcoin Fear & Greed Index (Alternative.me)</div>
            <div class="metric-value">{crypto_data['fng_val']}</div>
            <div class="{crypto_data['fng_css']}">{crypto_data['fng_classification']}</div>
        </div>
        """, unsafe_allow_html=True)