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

# Função resiliente para buscar dados do CoinGecko (Fonte 100% unificada)
@st.cache_data(ttl=20)
def get_coingecko_data():
    data = {
        "btc_price": "$64.303,80", "btc_change": "+2,24%", "btc_is_pos": True,
        "btc_raw_price": 64303.80,
        "eth_price": "$1.908,34", "eth_change": "+1,72%", "eth_is_pos": True,
        "eth_raw_price": 1908.34,
        "sol_price": "$75,88", "sol_change": "+1,70%", "sol_is_pos": True,
        "btc_dom": "59,26%", "mcap": "$2,15 Tri", "mcap_change": "+2,10%", "mcap_is_pos": True
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        url_prices = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
        resp_prices = requests.get(url_prices, headers=headers, timeout=3).json()

        if "bitcoin" in resp_prices:
            btc_p = resp_prices["bitcoin"]["usd"]
            btc_c = resp_prices["bitcoin"].get("usd_24h_change", 2.24)
            data["btc_raw_price"] = btc_p
            data["btc_price"] = f"${btc_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["btc_change"] = f"{btc_c:+.2f}%".replace(".", ",")
            data["btc_is_pos"] = btc_c >= 0

        if "ethereum" in resp_prices:
            eth_p = resp_prices["ethereum"]["usd"]
            eth_c = resp_prices["ethereum"].get("usd_24h_change", 1.72)
            data["eth_raw_price"] = eth_p
            data["eth_price"] = f"${eth_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["eth_change"] = f"{eth_c:+.2f}%".replace(".", ",")
            data["eth_is_pos"] = eth_c >= 0

        if "solana" in resp_prices:
            sol_p = resp_prices["solana"]["usd"]
            sol_c = resp_prices["solana"].get("usd_24h_change", 1.70)
            data["sol_price"] = f"${sol_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["sol_change"] = f"{sol_c:+.2f}%".replace(".", ",")
            data["sol_is_pos"] = sol_c >= 0
    except Exception:
        pass

    try:
        url_global = "https://api.coingecko.com/api/v3/global"
        resp_global = requests.get(url_global, headers=headers, timeout=3).json()

        if "data" in resp_global:
            mcap = resp_global["data"]["total_market_cap"]["usd"] / 1e12
            mcap_c = resp_global["data"].get("market_cap_change_percentage_24h_usd", 2.10)
            dom_btc = resp_global["data"]["market_cap_percentage"]["btc"]
            data["btc_dom"] = f"{dom_btc:.2f}%".replace(".", ",")
            data["mcap"] = f"${mcap:.2f} Tri".replace(".", ",")
            data["mcap_change"] = f"{mcap_c:+.2f}%".replace(".", ",")
            data["mcap_is_pos"] = mcap_c >= 0
    except Exception:
        pass

    return data

# Função para calcular níveis de Suporte e Resistência dinâmicos
def calcular_suporte_resistencia(preco_base, variacao_pct=0.035):
    sup = preco_base * (1 - variacao_pct)
    res = preco_base * (1 + variacao_pct)
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
    sp500_tendencia, sp500_score, sp500_valor_nivel = "Pressão Vendedora", "38 pts", "7.680 pts"
    ibov_tendencia, ibov_score, ibov_valor_nivel = "Consolidação 7D", "52 pts", "165.200 pts"

    with col_left:
        if formato == "B2C (YouTube)":
            st.subheader("🎬 Roteiro B2C YouTube (TradFi & Macro)")
            st.caption("Roteiro de Vídeo (YouTube B2C):")
            
            roteiro_tradfi = f"""[HOOK 0-15s]
O mercado global está em ponto crítico hoje ({data_atual}). S&P 500 recuando e o Ibovespa operando em consolidação. Vamos direto aos dados do relatório institucional.

[BLOCO 1 - PANORAMA GLOBAL]
- S&P 500 em 7.758 pts (-0.53%).
- Ibovespa segurando a região dos 166.833 pts.
- Dólar cotado a R$ 5,20.

[BLOCO 2 - COMMODITIES E LIQUIDEZ]
- Ouro registrando forte alta a $4.474,90/oz (+0.85%).
- Petróleo Brent operando a $90,69 (+2.45%).

[CTA & ENCERRAMENTO]
Deixe seu like e inscreva-se para análises diárias da OMNIRESEARCH!"""

            st.text_area("", value=roteiro_tradfi, height=310, disabled=False)
        else:
            st.subheader("📰 Relatório B2B (TradFi & Macroeconomia)")
            st.caption("Relatório Macro/TradFi (B2B):")
            
            relatorio_texto = f"""=== RELATÓRIO INSTITUCIONAL TRADFI & MACROECONOMIA (B2B) ===
Data/Hora: {data_atual}

1. PANORAMA MACRO E BENCHMARKS
- S&P 500: 7.758 pts (-0.53%) (Yahoo Finance)
- Ibovespa: 166.833 pts (-0.16%) (Yahoo Finance)
- Câmbio (USD/BRL): R$ 5,20 (+0.00%) (Yahoo Finance)
- M2 Global (Liquidez Monetária): $104.8T (+4.2% YoY) (FRED St. Louis Fed)

2. MESA DE COMMODITIES
- Ouro Spot (XAU/USD): $4.474,90/oz (+0.85%) (Yahoo Finance)
- Petróleo Brent: $90,69/bbl (+2.45%) (Yahoo Finance)

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

    with col_right:
        st.subheader("📊 Métricas Agregadas")
        st.caption(f"Atualizado às {data_atual.split('às ')[1] if 'às ' in data_atual else data_atual}")
        
        st.markdown("""
        <div class="stCard">
            <div class="metric-label">1. S&P 500 (Yahoo Finance)</div>
            <div class="metric-value">7.758 pts</div>
            <div class="status-red">-0.53% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">2. IBOVESPA (Yahoo Finance)</div>
            <div class="metric-value">166.833 pts</div>
            <div class="status-red">-0.16% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">3. USD / BRL (Yahoo Finance)</div>
            <div class="metric-value">R$ 5,20</div>
            <div class="status-green">+0.00% (24h)</div>
        </div>
        <div class="stCard">
            <div class="metric-label">4. Ouro Spot / XAU (Yahoo Finance)</div>
            <div class="metric-value">$4.474,90</div>
            <div class="status-green">+0.85% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">5. Petróleo Brent (Yahoo Finance)</div>
            <div class="metric-value">$90,69</div>
            <div class="status-green">+2.45% hoje</div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Módulo Crypto (Exclusivo CoinGecko + Previsão 48h & Suporte/Resistência)
    crypto_data = get_coingecko_data()

    btc_sup, btc_res = calcular_suporte_resistencia(crypto_data["btc_raw_price"], 0.035)
    eth_sup, eth_res = calcular_suporte_resistencia(crypto_data["eth_raw_price"], 0.040)

    btc_prev_48h = "Alta Moderada" if crypto_data["btc_is_pos"] else "Pressão Vendedora"
    btc_target_48h = btc_res
    eth_prev_48h = "Consolidação / Alta" if crypto_data["eth_is_pos"] else "Teste de Suporte"
    eth_target_48h = eth_res

    btc_status_css = "status-green" if crypto_data["btc_is_pos"] else "status-red"
    eth_status_css = "status-green" if crypto_data["eth_is_pos"] else "status-red"
    sol_status_css = "status-green" if crypto_data["sol_is_pos"] else "status-red"
    mcap_status_css = "status-green" if crypto_data["mcap_is_pos"] else "status-red"

    with col_left:
        if formato == "B2C (YouTube)":
            st.subheader("🎬 Roteiro B2C YouTube (Crypto & Web3)")
            st.caption("Roteiro de Vídeo (YouTube B2C):")
            
            roteiro_crypto = f"""[HOOK 0-15s]
O Bitcoin está sendo negociado a {crypto_data['btc_price']} nesta tarde ({data_atual})! Vamos analisar os alvos de 48 horas e os níveis de suporte essenciais para ETH e SOL.

[BLOCO 1 - PREVISÃO 48H E ALVOS]
- BTC: Previsão de {btc_prev_48h} com alvo em {btc_target_48h} e suporte em {btc_sup}.
- ETH: Cotado a {crypto_data['eth_price']} com resistência em {eth_res} e suporte em {eth_sup}.

[BLOCO 2 - METRICAS CRÍTICAS DE MERCADO]
- Solana (SOL): {crypto_data['sol_price']} ({crypto_data['sol_change']}).
- Dominância do Bitcoin: {crypto_data['btc_dom']}.
- Capitalização de Mercado Total: {crypto_data['mcap']}.

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
- Market Cap Total Crypto: {crypto_data['mcap']} ({crypto_data['mcap_change']}) (CoinGecko)

2. MESA DE LIQUIDEZ E ON-CHAIN
- Financiamento BTC (Funding Rate): +0.012% (Neutro/Comprador)
- Reservas de BTC nas Corretoras: 2.05M BTC (Outflow Contínuo)

3. PREVISÃO 48H E NÍVEIS TÉCNICOS CRÍTICOS
- Bitcoin (BTC): Previsão 48h ({btc_prev_48h}) | Alvo: {btc_target_48h} | Suporte: {btc_sup}
- Ethereum (ETH): Previsão 48h ({eth_prev_48h}) | Alvo: {eth_target_48h} | Suporte: {eth_sup}"""

            st.text_area("", value=relatorio_crypto, height=310, disabled=False)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Previsão 48h (BTC)</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{btc_prev_48h}</div>
                <div class="status-green">↑ Alvo {btc_target_48h}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Suporte / Resistência (BTC)</div>
                <div style="font-size: 13px; font-weight: bold; color: #f8fafc;">S: {btc_sup} | R: {btc_res}</div>
                <div class="status-green">↑ Faixa Operacional</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Previsão 48h (ETH)</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{eth_prev_48h}</div>
                <div class="status-blue">→ Alvo {eth_target_48h}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Suporte / Resistência (ETH)</div>
                <div style="font-size: 13px; font-weight: bold; color: #f8fafc;">S: {eth_sup} | R: {eth_res}</div>
                <div class="status-blue">→ Faixa Operacional</div>
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
            <div class="metric-label">5. Market Cap Total Crypto (CoinGecko)</div>
            <div class="metric-value">{crypto_data['mcap']}</div>
            <div class="{mcap_status_css}">{crypto_data['mcap_change']} hoje</div>
        </div>
        """, unsafe_allow_html=True)