import streamlit as st

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

# Timestamp do Dashboard
data_atual = "17/08/2026 às 14:44:16 BRT"

# Função para lógica condicional de Níveis Técnicos
def calcular_nivel_condicional(estado):
    estado_clean = estado.lower()
    if "bullish" in estado_clean or "compradora" in estado_clean:
        return "Próxima Resistência", "status-green", "↑"
    elif "bearish" in estado_clean or "vendedora" in estado_clean:
        return "Próximo Suporte", "status-red", "↓"
    else:
        return "Suporte Atual", "status-blue", "→"

# Sidebar - Configurações OMNI
st.sidebar.title("⚙️ Configurações OMNI")
st.sidebar.caption("Controle de geração de roteiros e relatórios")

idioma = st.sidebar.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English (US)"])

modulo = st.sidebar.radio(
    "💡 Escolha o Módulo:",
    ["Crypto", "TradFi (Macro)"],
    index=1,
    help="Selecione o segmento de análise"
)

formato = st.sidebar.radio(
    f"🎯 Formato ({modulo}):",
    ["B2B (Relatório)", "B2C (YouTube)"],
    index=0,
    help="Escolha o tipo de entregável"
)

st.sidebar.info("💡 O modo Auto-Pilot está disponível exclusivamente para entregáveis B2C (YouTube).")

# Header Principal
st.title("⚡ OMNIRESEARCH Engine")
st.caption("Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

# Banner de Timestamp
st.info(f"🕒 **Dados consolidados das {data_atual}**")

# Layout Principal em Duas Colunas
col_left, col_right = st.columns([1.6, 1])

# LOGICA DINÂMICA BASEADA NO MÓDULO SELECIONADO
if modulo == "TradFi (Macro)":
    # Módulo TradFi
    sp500_tendencia, sp500_score, sp500_estado, sp500_valor_nivel = "Pressão Vendedora", "38 pts", "bearish", "7.680 pts"
    ibov_tendencia, ibov_score, ibov_estado, ibov_valor_nivel = "Consolidação 7D", "52 pts", "neutro", "165.200 pts"
    
    sp500_rotulo, sp500_css, sp500_seta = calcular_nivel_condicional(sp500_estado)
    ibov_rotulo, ibov_css, ibov_seta = calcular_nivel_condicional(ibov_estado)

    with col_left:
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
- S&P 500 (EUA): Tendência 7D ({sp500_tendencia} - {sp500_score}) | {sp500_rotulo}: {sp500_valor_nivel}
- Ibovespa (Brasil): Tendência 7D ({ibov_tendencia} - {ibov_score}) | {ibov_rotulo}: {ibov_valor_nivel}"""

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
                <div class="metric-label">{sp500_rotulo} (S&P 500)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{sp500_valor_nivel}</div>
                <div class="{sp500_css}">{sp500_seta} Nível Crítico</div>
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
                <div class="metric-label">{ibov_rotulo} (Ibovespa)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{ibov_valor_nivel}</div>
                <div class="{ibov_css}">{ibov_seta} Nível Crítico</div>
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
    # Módulo Crypto
    btc_tendencia, btc_score, btc_estado, btc_valor_nivel = "Tendência Compradora", "78 pts", "bullish", "$66.500"
    eth_tendencia, eth_score, eth_estado, eth_valor_nivel = "Consolidação 7D", "54 pts", "neutro", "$3.380"
    
    btc_rotulo, btc_css, btc_seta = calcular_nivel_condicional(btc_estado)
    eth_rotulo, eth_css, eth_seta = calcular_nivel_condicional(eth_estado)

    with col_left:
        st.subheader("📰 Relatório B2B (Crypto & Web3)")
        st.caption("Relatório Crypto/Web3 (B2B):")
        
        relatorio_crypto = f"""=== RELATÓRIO INSTITUCIONAL CRYPTO & WEB3 (B2B) ===
Data/Hora: {data_atual}

1. CRIPTO PANORAMA E BENCHMARKS
- Bitcoin (BTC/USDT): $64.284,27 (+2.20%) (Binance)
- Ethereum (ETH/USDT): $3.450,10 (+1.80%) (Binance)
- Solana (SOL/USDT): $148,50 (+4.50%) (Binance)
- Dominância do Bitcoin (BTC.D): 56.4% (+0.3%) (TradingView)
- Market Cap Total Crypto: $2.35T (+2.10%) (CoinGecko)

2. MESA DE LIQUIDEZ E ON-CHAIN
- Financiamento BTC (Funding Rate): +0.012% (Neutro/Comprador)
- Reservas de BTC nas Corretoras: 2.05M BTC (Outflow Contínuo)

3. VETORES PREDITIVOS E NÍVEIS TÉCNICOS
- Bitcoin (BTC): Tendência 7D ({btc_tendencia} - {btc_score}) | {btc_rotulo}: {btc_valor_nivel}
- Ethereum (ETH): Tendência 7D ({eth_tendencia} - {eth_score}) | {eth_rotulo}: {eth_valor_nivel}"""

        st.text_area("", value=relatorio_crypto, height=310, disabled=False)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Tendência 7D (BTC)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{btc_tendencia}</div>
                <div class="status-green">↑ {btc_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">{btc_rotulo} (BTC)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{btc_valor_nivel}</div>
                <div class="{btc_css}">{btc_seta} Nível Crítico</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">Tendência 7D (ETH)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{eth_tendencia}</div>
                <div class="status-blue">→ {eth_score}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stCard">
                <div class="metric-label">{eth_rotulo} (ETH)</div>
                <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">{eth_valor_nivel}</div>
                <div class="{eth_css}">{eth_seta} Nível Crítico</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.subheader("📊 Métricas Agregadas (Crypto)")
        st.caption(f"Atualizado às {data_atual.split('às ')[1] if 'às ' in data_atual else data_atual}")
        
        st.markdown("""
        <div class="stCard">
            <div class="metric-label">1. Bitcoin / USDT (Binance)</div>
            <div class="metric-value">$64.284,27</div>
            <div class="status-green">+2.20% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">2. Ethereum / USDT (Binance)</div>
            <div class="metric-value">$3.450,10</div>
            <div class="status-green">+1.80% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">3. Solana / USDT (Binance)</div>
            <div class="metric-value">$148,50</div>
            <div class="status-green">+4.50% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">4. Dominância BTC (BTC.D)</div>
            <div class="metric-value">56,4%</div>
            <div class="status-green">+0.30% hoje</div>
        </div>
        <div class="stCard">
            <div class="metric-label">5. Market Cap Total Crypto</div>
            <div class="metric-value">$2,35 Tri</div>
            <div class="status-green">+2.10% hoje</div>
        </div>
        """, unsafe_allow_html=True)