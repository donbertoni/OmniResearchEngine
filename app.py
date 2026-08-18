import streamlit as st

# Configuração Inicial da Página
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada Coesa (CSS)
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Header e Banner */
    .info-banner {
        background-color: #1a2638;
        border: 1px solid #23354d;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 13px;
        color: #8bb4e7;
        margin-bottom: 20px;
    }

    /* Cards de Métricas e Categorias */
    .metric-card {
        background-color: #131924;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 20px;
        font-weight: bold;
        color: #f8fafc;
    }
    .metric-change-positive {
        font-size: 12px;
        color: #10b981;
        font-weight: 600;
    }
    .metric-change-negative {
        font-size: 12px;
        color: #ef4444;
        font-weight: 600;
    }

    /* Sub-Cards do Relatório */
    .sub-card {
        background-color: #131924;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 10px;
        text-align: center;
    }
    .sub-card-label {
        font-size: 11px;
        color: #94a3b8;
    }
    .sub-card-val {
        font-size: 13px;
        font-weight: bold;
        color: #f8fafc;
        margin-top: 2px;
    }

    /* Blocos de Categoria do Rodapé */
    .cat-card {
        background-color: #131924;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 16px;
        min-height: 185px;
    }
    .cat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 8px;
        margin-bottom: 10px;
    }
    .cat-title {
        font-size: 14px;
        font-weight: bold;
        color: #38bdf8;
    }
    .cat-badge {
        font-size: 10px;
        background-color: #1e293b;
        color: #38bdf8;
        padding: 2px 6px;
        border-radius: 4px;
    }
    .cat-row {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-bottom: 6px;
        color: #94a3b8;
    }
    .cat-row-val {
        color: #f8fafc;
        font-weight: 600;
    }

    /* Status Auto-Pilot */
    .autopilot-box {
        background-color: #0f291e;
        border: 1px solid #10b981;
        border-radius: 6px;
        padding: 10px;
        margin-top: 10px;
        font-size: 12px;
        color: #34d399;
    }
</style>
""", unsafe_allow_html=True)

# BARRA LATERAL (Sidebar)
with st.sidebar:
    st.title("⚙️ Configurações OMNI")
    st.caption("Controle de geração de roteiros e relatórios")
    
    st.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English (US)"], index=0)
    modulo = st.radio("💡 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=0)
    
    st.divider()
    
    st.subheader("🎛️ Calibragem (SaaS Enterprise)")
    st.caption("Selecione os setores/categorias:")
    
    cat_etf = st.checkbox("1 - ETF's", value=True)
    cat_treasury = st.checkbox("2 - Treasury", value=True)
    cat_mineracao = st.checkbox("3 - Mineração e Hashrate", value=True)
    cat_spot = st.checkbox("4 - Volume Spot (24 hs)", value=True)
    cat_futuros = st.checkbox("5 - Volume Futuros (24 hs)", value=True)
    cat_oi = st.checkbox("6 - Open Interest", value=True)
    cat_defi = st.checkbox("7 - DeFi e Layer 1s", value=True)
    cat_stable = st.checkbox("8 - Stablecoins", value=True)
    
    st.divider()
    
    formato = st.radio("🎯 Formato (Crypto):", ["B2B (Relatório)", "B2C (YouTube)"], index=0)
    
    # REATIVAÇÃO E CONTROLE DO AUTO-PILOT
    st.subheader("🤖 Automação & Auto-Pilot")
    auto_pilot = st.toggle("Ativar Modo Auto-Pilot", value=(formato == "B2C (YouTube)"))
    
    if auto_pilot:
        st.markdown("""
        <div class="autopilot-box">
            ⚡ <strong>Auto-Pilot Ativo</strong><br/>
            Pipeline automático executando coleta de dados, síntese B2B e geração de roteiros/vídeos HITL.
        </div>
        """, unsafe_allow_html=True)
        freq_auto = st.select_slider("Frequência de disparo:", options=["1h", "4h", "12h", "24h"], value="4h")
    else:
        st.info("✋ Modo Manual / Human-In-The-Loop (HITL) selecionado.")

# ÁREA PRINCIPAL DA DASHBOARD
st.markdown("# ⚡ OMNIRESEARCH Engine")
st.markdown("**Plataforma Integrada de Inteligência Financeira:** YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

# Banner de Status da Atualização
st.markdown("""
<div class="info-banner">
    🕒 <strong>Dados consolidados das 18/08/2026 às 10:39:42 BRT</strong> &nbsp;|&nbsp; 
    Status da API: <span style="color:#10b981;">● Online</span> &nbsp;|&nbsp; 
    Módulo Ativo: <strong>{}</strong>
</div>
""".format(modulo), unsafe_allow_html=True)

# VISÃO DASHBOARD SUPERIOR (Relatório B2B + Métricas Agregadas)
col_left, col_right = st.columns([1.65, 1], gap="medium")

with col_left:
    st.markdown("### 📄 Relatório B2B (Crypto & Web3)")
    st.caption("Relatório Crypto/Web3 (B2B) com os 32 indicadores integrados ao exportável:")
    
    report_text = """=== RELATÓRIO INSTITUCIONAL CRYPTO & WEB3 (B2B) ===
Data/Hora: 18/08/2026 às 10:39:42 BRT

1. CRIPTO PANORAMA E BENCHMARKS
- Bitcoin (BTC/USDT): $64.481,00 (+2,19%) (CoinGecko)
- Ethereum (ETH/USDT): $1.909,21 (+1,36%) (CoinGecko)
- Solana (SOL/USDT): $76,05 (+1,25%) (CoinGecko)
- Dominância do Bitcoin (BTC.D): 56,56% (+0,63%) (CoinGecko)
- Bitcoin Fear & Greed Index: 41 / 100 (Medo) (Alternative.me)

2. MESA DE LIQUIDEZ E ON-CHAIN
- Financiamento BTC (Funding Rate): +0.012% (Neutro/Comprador)
- Reservas de BTC nas Corretoras: 2.05M BTC (Outflow Contínuo)

3. VETORES PREDITIVOS E NÍVEIS TÉCNICOS (BITCOIN)
- Tendência 7D (BTC): Tendência Compradora (78 pts)"""

    st.text_area(
        label="Relatório",
        value=report_text,
        height=265,
        label_visibility="collapsed"
    )
    
    # Quadrado/Barra de Resumo abaixo do Report
    sub1, sub2, sub3, sub4 = st.columns(4)
    with sub1:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Tendência 7D (BTC)</div>
            <div class="sub-card-val">Compradora</div>
            <div style="font-size:11px; color:#10b981; font-weight:600;">↑ 78 pts</div>
        </div>
        """, unsafe_allow_html=True)
    with sub2:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Resistência (BTC)</div>
            <div class="sub-card-val">$65.000</div>
            <div style="font-size:11px; color:#10b981; font-weight:600;">↑ Nível Crítico</div>
        </div>
        """, unsafe_allow_html=True)
    with sub3:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Suporte Crítico</div>
            <div class="sub-card-val">$62.500</div>
            <div style="font-size:11px; color:#ef4444; font-weight:600;">↓ Zona Defesa</div>
        </div>
        """, unsafe_allow_html=True)
    with sub4:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Previsão 48h</div>
            <div class="sub-card-val">Alta Moderada</div>
            <div style="font-size:11px; color:#38bdf8; font-weight:600;">↑ Alvo $65k</div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("### 📊 Métricas Agregadas (Crypto)")
    st.caption("Atualizado às 10:39:42 BRT")
    
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">1. Bitcoin / USDT (CoinGecko)</div>
        <div class="metric-value">$64.481,00</div>
        <div class="metric-change-positive">+2,19% hoje</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">2. Ethereum / USDT (CoinGecko)</div>
        <div class="metric-value">$1.909,21</div>
        <div class="metric-change-positive">+1,36% hoje</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">3. Solana / USDT (CoinGecko)</div>
        <div class="metric-value">$76,05</div>
        <div class="metric-change-positive">+1,25% hoje</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">4. Dominância BTC (CoinGecko)</div>
        <div class="metric-value">56,56%</div>
        <div class="metric-change-positive">+0,63% hoje</div>
    </div>
    
    <div class="metric-card">
        <div class="metric-title">5. Bitcoin Fear & Greed Index (Alternative.me)</div>
        <div class="metric-value">41 / 100</div>
        <div class="metric-change-negative" style="color: #f59e0b;">Medo</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# SEÇÃO INFERIOR: BLOCOS DAS 8 CATEGORIAS INTEGRADAS AO DASHBOARD
st.markdown("### 📁 Painel de Análise Integrada das 8 Categorias")
st.caption("Métricas detalhadas e consolidadas diretamente com os dados do relatório acima:")

# Estrutura com dados 100% conectados com o relatório principal
categories = [
    {
        "active": cat_etf,
        "title": "1. ETF's (Spot & Inst.)",
        "badge": "Institutional",
        "data": [
            ("Entrada Líquida Diária", "+$248.5M"),
            ("AUM Total Spot ETFs", "$58.4B"),
            ("Atividade IBIT / FBTC", "Acumulação Alta"),
            ("Fluxo Líquido (7D)", "+$1.12B")
        ]
    },
    {
        "active": cat_treasury,
        "title": "2. Treasury & Tesourarias",
        "badge": "Corporate",
        "data": [
            ("MicroStrategy Holdings", "226.500 BTC"),
            ("Compras 7D Corporativo", "+$12.4M"),
            ("Dominância no Circulante", "3,15%"),
            ("Reservas em Balanço", "Estáveis")
        ]
    },
    {
        "active": cat_mineracao,
        "title": "3. Mineração & Hashrate",
        "badge": "On-Chain",
        "data": [
            ("Hashrate Agregado", "642 EH/s"),
            ("Hashprice (TH/dia)", "$0,048 USD"),
            ("Dificuldade Atual", "86.8 T"),
            ("Estresse Mineradores", "Neutro")
        ]
    },
    {
        "active": cat_spot,
        "title": "4. Volume Spot (24 hs)",
        "badge": "Market Data",
        "data": [
            ("BTC / USDT Spot Price", "$64.481,00"),
            ("ETH / USDT Spot Price", "$1.909,21"),
            ("SOL / USDT Spot Price", "$76,05"),
            ("Volume Global 24h", "$28.4B")
        ]
    },
    {
        "active": cat_futuros,
        "title": "5. Volume Futuros (24 hs)",
        "badge": "Derivatives",
        "data": [
            ("Volume Derivados 24h", "$89.2B"),
            ("Funding Rate BTC", "+0.012%"),
            ("Viés de Financiamento", "Neutro/Comprador"),
            ("Proporção Longs", "52,4%")
        ]
    },
    {
        "active": cat_oi,
        "title": "6. Open Interest (OI)",
        "badge": "Derivatives",
        "data": [
            ("Open Interest Total", "$32.1B"),
            ("CME Market Share", "30,5% ($9.8B)"),
            ("Nível de Alavancagem", "Moderado"),
            ("Risco de Liquidação", "Baixo")
        ]
    },
    {
        "active": cat_defi,
        "title": "7. DeFi & Layer 1s",
        "badge": "Ecosystem",
        "data": [
            ("Dominância Bitcoin", "56,56% (+0,63%)"),
            ("TVL Agregado DeFi", "$84.2B"),
            ("Solana DEX Volume", "$1.82B"),
            ("Taxa Gas Ethereum", "12 Gwei")
        ]
    },
    {
        "active": cat_stable,
        "title": "8. Stablecoins & Liquidez",
        "badge": "Liquidity",
        "data": [
            ("Reservas Corretoras", "2.05M BTC"),
            ("Tendência de Reservas", "Outflow Contínuo"),
            ("Fear & Greed Index", "41 / 100 (Medo)"),
            ("Poder de Compra USDT", "Elevado")
        ]
    }
]

# Filtragem de categorias selecionadas na calibragem
active_cats = [c for c in categories if c["active"]]

if active_cats:
    # Organização visual em grid de 4 colunas por linha
    for i in range(0, len(active_cats), 4):
        cols = st.columns(4)
        group = active_cats[i:i+4]
        for col, cat in zip(cols, group):
            with col:
                rows_html = "".join([
                    f'<div class="cat-row"><span>{label}:</span><span class="cat-row-val">{val}</span></div>'
                    for label, val in cat["data"]
                ])
                st.markdown(f"""
                <div class="cat-card">
                    <div class="cat-header">
                        <span class="cat-title">{cat["title"]}</span>
                        <span class="cat-badge">{cat["badge"]}</span>
                    </div>
                    {rows_html}
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("Nenhuma categoria selecionada no painel de calibragem da barra lateral.")