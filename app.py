import streamlit as st

# Configuração Inicial da Página
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Banner Superior de Informações */
    .info-banner {
        background-color: #1a2638;
        border: 1px solid #23354d;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 13px;
        color: #8bb4e7;
        margin-bottom: 20px;
    }

    /* Cards de Métricas e Agregados */
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
    .metric-change-neutral {
        font-size: 12px;
        color: #f59e0b;
        font-weight: 600;
    }

    /* Sub-cards no Rodapé do Relatório */
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

    /* Cards das 8 Categorias */
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

    /* Caixa de Aviso / Auto-Pilot */
    .autopilot-notice {
        background-color: #172554;
        border: 1px solid #1e40af;
        border-radius: 6px;
        padding: 12px;
        font-size: 12px;
        color: #93c5fd;
        margin-top: 15px;
    }
    .autopilot-active {
        background-color: #0f291e;
        border: 1px solid #10b981;
        border-radius: 6px;
        padding: 12px;
        font-size: 12px;
        color: #34d399;
        margin-top: 15px;
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
    
    if modulo == "Crypto":
        cat_1 = st.checkbox("1 - ETF's", value=True)
        cat_2 = st.checkbox("2 - Treasury", value=True)
        cat_3 = st.checkbox("3 - Mineração e Hashrate", value=True)
        cat_4 = st.checkbox("4 - Volume Spot (24 hs)", value=True)
        cat_5 = st.checkbox("5 - Volume Futuros (24 hs)", value=True)
        cat_6 = st.checkbox("6 - Open Interest", value=True)
        cat_7 = st.checkbox("7 - DeFi e Layer 1s", value=True)
        cat_8 = st.checkbox("8 - Stablecoins", value=True)
    else:
        cat_1 = st.checkbox("1 - Bancos e Seguradoras", value=True)
        cat_2 = st.checkbox("2 - Energia", value=True)
        cat_3 = st.checkbox("3 - Tech", value=True)
        cat_4 = st.checkbox("4 - Commodities", value=True)
        cat_5 = st.checkbox("5 - Varejo", value=True)
        cat_6 = st.checkbox("6 - Logística e Infra.", value=True)
        cat_7 = st.checkbox("7 - Agro e Indústria", value=True)
        cat_8 = st.checkbox("8 - Crypto e Digital", value=True)
    
    st.divider()
    
    formato = st.radio(f"🎯 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube)"], index=0)
    
    if formato == "B2B (Relatório)":
        st.markdown("""
        <div class="autopilot-notice">
            💡 O modo Auto-Pilot está disponível exclusivamente para entregáveis B2C (YouTube).
        </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("🤖 Automação & Auto-Pilot")
        auto_pilot = st.toggle("Ativar Modo Auto-Pilot", value=True)
        if auto_pilot:
            st.markdown("""
            <div class="autopilot-active">
                ⚡ <strong>Auto-Pilot Ativo</strong><br/>
                Pipeline automatizado para geração contínua de vídeos e roteiros B2C.
            </div>
            """, unsafe_allow_html=True)
            st.select_slider("Frequência de disparo:", options=["1h", "4h", "12h", "24h"], value="4h")

# ÁREA PRINCIPAL DA DASHBOARD
st.markdown("# ⚡ OMNIRESEARCH Engine")
st.markdown("**Plataforma Integrada de Inteligência Financeira:** YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

st.markdown(f"""
<div class="info-banner">
    🕒 <strong>Dados consolidados das 18/08/2026 às 10:39:42 BRT</strong> &nbsp;|&nbsp; 
    Status da API: <span style="color:#10b981;">● Online</span> &nbsp;|&nbsp; 
    Módulo Ativo: <strong>{modulo}</strong>
</div>
""", unsafe_allow_html=True)

# LÓGICA DE EXIBIÇÃO POR MÓDULO
if modulo == "Crypto":
    report_title = "📄 Relatório B2B (Crypto & Web3)"
    metrics_title = "📊 Métricas Agregadas (Crypto)"
    
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

    sub_cards_data = [
        ("Tendência 7D (BTC)", "Compradora", "↑ 78 pts", "#10b981"),
        ("Resistência (BTC)", "$65.000", "↑ Nível Crítico", "#10b981"),
        ("Suporte Crítico", "$62.500", "↓ Zona Defesa", "#ef4444"),
        ("Previsão 48h", "Alta Moderada", "↑ Alvo $65k", "#38bdf8")
    ]

    metrics_list = [
        ("1. Bitcoin / USDT (CoinGecko)", "$64.481,00", "+2,19% hoje", "#10b981"),
        ("2. Ethereum / USDT (CoinGecko)", "$1.909,21", "+1,36% hoje", "#10b981"),
        ("3. Solana / USDT (CoinGecko)", "$76,05", "+1,25% hoje", "#10b981"),
        ("4. Dominância BTC (CoinGecko)", "56,56%", "+0,63% hoje", "#10b981"),
        ("5. Bitcoin Fear & Greed Index", "41 / 100", "Medo", "#f59e0b")
    ]

    categories = [
        {"active": cat_1, "title": "1. ETF's (Spot & Inst.)", "badge": "Institutional", "data": [("Entrada Líquida Diária", "+$248.5M"), ("AUM Total Spot ETFs", "$58.4B"), ("Atividade IBIT / FBTC", "Acumulação Alta"), ("Fluxo Líquido (7D)", "+$1.12B")]},
        {"active": cat_2, "title": "2. Treasury & Tesourarias", "badge": "Corporate", "data": [("MicroStrategy Holdings", "226.500 BTC"), ("Compras 7D Corporativo", "+$12.4M"), ("Dominância no Circulante", "3,15%"), ("Reservas em Balanço", "Estáveis")]},
        {"active": cat_3, "title": "3. Mineração & Hashrate", "badge": "On-Chain", "data": [("Hashrate Agregado", "642 EH/s"), ("Hashprice (TH/dia)", "$0,048 USD"), ("Dificuldade Atual", "86.8 T"), ("Estresse Mineradores", "Neutro")]},
        {"active": cat_4, "title": "4. Volume Spot (24 hs)", "badge": "Market Data", "data": [("BTC / USDT Spot Price", "$64.481,00"), ("ETH / USDT Spot Price", "$1.909,21"), ("SOL / USDT Spot Price", "$76,05"), ("Volume Global 24h", "$28.4B")]},
        {"active": cat_5, "title": "5. Volume Futuros (24 hs)", "badge": "Derivatives", "data": [("Volume Derivados 24h", "$89.2B"), ("Funding Rate BTC", "+0.012%"), ("Viés de Financiamento", "Neutro/Comprador"), ("Proporção Longs", "52,4%")]},
        {"active": cat_6, "title": "6. Open Interest (OI)", "badge": "Derivatives", "data": [("Open Interest Total", "$32.1B"), ("CME Market Share", "30,5% ($9.8B)"), ("Nível de Alavancagem", "Moderado"), ("Risco de Liquidação", "Baixo")]},
        {"active": cat_7, "title": "7. DeFi & Layer 1s", "badge": "Ecosystem", "data": [("Dominância Bitcoin", "56,56% (+0,63%)"), ("TVL Agregado DeFi", "$84.2B"), ("Solana DEX Volume", "$1.82B"), ("Taxa Gas Ethereum", "12 Gwei")]},
        {"active": cat_8, "title": "8. Stablecoins & Liquidez", "badge": "Liquidity", "data": [("Reservas Corretoras", "2.05M BTC"), ("Tendência de Reservas", "Outflow Contínuo"), ("Fear & Greed Index", "41 / 100 (Medo)"), ("Poder de Compra USDT", "Elevado")]}
    ]

else:  # TRADFI (MACRO)
    report_title = "📄 Relatório B2B (TradFi & Macro)"
    metrics_title = "📊 Métricas Agregadas (TradFi & Macro)"
    
    report_text = """=== RELATÓRIO INSTITUCIONAL TRADFI & MACRO (B2B) ===
Data/Hora: 18/08/2026 às 10:39:42 BRT

1. BANCOS E SEGURADORAS
- ITUB4: R$ 34,20 (+0,85%)
- BBAS3: R$ 28,15 (+1,12%)
- BBDC4: R$ 15,40 (+0,40%)
- BBSE3: R$ 33,90 (+0,30%)

2. ENERGIA
- PETR4: R$ 38,50 (+1,45%)
- PRIO3: R$ 46,10 (+0,90%)
- EQTL3: R$ 31,80 (+0,25%)
- CPFE3: R$ 34,60 (+0,15%)

3. TECH
- TOTVS3: R$ 29,40 (+0,60%)
- NVDA: $ 128,50 (+2,30%)
- AAPL: $ 224,10 (+0,80%)
- MSFT: $ 448,20 (+1,10%)

4. COMMODITIES
- VALE3: R$ 61,80 (-0,45%)
- GGBR4: R$ 19,10 (+0,20%)
- CMIG4: R$ 11,25 (+0,50%)
- KLBN11: R$ 21,80 (-0,10%)"""

    sub_cards_data = [
        ("Tendência TradFi", "Compradora", "↑ 68 pts", "#10b981"),
        ("Destaque Setorial", "Bancos & Tech", "↑ Forte Fluxo", "#10b981"),
        ("Risco Macro", "Moderado", "↔ Inflação/Juros", "#f59e0b"),
        ("Previsão 48h", "Alta Moderada", "↑ Consolidação", "#38bdf8")
    ]

    metrics_list = [
        ("1. ITUB4 (Itaú Unibanco)", "R$ 34,20", "+0,85% hoje", "#10b981"),
        ("2. PETR4 (Petrobras)", "R$ 38,50", "+1,45% hoje", "#10b981"),
        ("3. NVDA (Nvidia Corp)", "$ 128,50", "+2,30% hoje", "#10b981"),
        ("4. VALE3 (Vale S.A.)", "R$ 61,80", "-0,45% hoje", "#ef4444"),
        ("5. WEGE3 (WEG S.A.)", "R$ 52,10", "+1,15% hoje", "#10b981")
    ]

    categories = [
        {"active": cat_1, "title": "1. Bancos e Seguradoras", "badge": "Banking & Ins.", "data": [("ITUB4", "R$ 34,20 (+0,85%)"), ("BBAS3", "R$ 28,15 (+1,12%)"), ("BBDC4", "R$ 15,40 (+0,40%)"), ("BBSE3", "R$ 33,90 (+0,30%)")]},
        {"active": cat_2, "title": "2. Energia", "badge": "Energy", "data": [("PETR4", "R$ 38,50 (+1,45%)"), ("PRIO3", "R$ 46,10 (+0,90%)"), ("EQTL3", "R$ 31,80 (+0,25%)"), ("CPFE3", "R$ 34,60 (+0,15%)")]},
        {"active": cat_3, "title": "3. Tech", "badge": "Technology", "data": [("TOTVS3", "R$ 29,40 (+0,60%)"), ("NVDA", "$ 128,50 (+2,30%)"), ("AAPL", "$ 224,10 (+0,80%)"), ("MSFT", "$ 448,20 (+1,10%)")]},
        {"active": cat_4, "title": "4. Commodities", "badge": "Commodities", "data": [("VALE3", "R$ 61,80 (-0,45%)"), ("GGBR4", "R$ 19,10 (+0,20%)"), ("CMIG4", "R$ 11,25 (+0,50%)"), ("KLBN11", "R$ 21,80 (-0,10%)")]},
        {"active": cat_5, "title": "5. Varejo", "badge": "Retail", "data": [("ASAI3", "R$ 12,40 (+0,70%)"), ("LREN3", "R$ 17,80 (-0,30%)"), ("MGLU3", "R$ 13,10 (+1,50%)"), ("RADL3", "R$ 26,50 (+0,40%)")]},
        {"active": cat_6, "title": "6. Logística e Infra.", "badge": "Infra & Log", "data": [("RAIL3", "R$ 22,30 (+0,80%)"), ("WEGE3", "R$ 52,10 (+1,15%)"), ("CCRO3", "R$ 13,60 (+0,10%)"), ("EMBR3", "R$ 41,20 (+1,80%)")]},
        {"active": cat_7, "title": "7. Agro e Indústria", "badge": "Agri & Industry", "data": [("SLCE3", "R$ 18,90 (+0,30%)"), ("BRFS3", "R$ 23,40 (+1,20%)"), ("ABEV3", "R$ 12,85 (+0,15%)"), ("JBSS3", "R$ 35,60 (+0,95%)")]},
        {"active": cat_8, "title": "8. Crypto e Digital", "badge": "Digital Assets", "data": [("BTCUSDT", "$ 64.481,00 (+2,19%)"), ("ETHUSDT", "$ 1.909,21 (+1,36%)"), ("SOLUSDT", "$ 76,05 (+1,25%)"), ("BNBUSDT", "$ 582,40 (+0,90%)")]}
    ]

# RENDERIZAÇÃO
col_left, col_right = st.columns([1.65, 1], gap="medium")

with col_left:
    st.markdown(f"### {report_title}")
    st.caption("Relatório com indicadores integrados ao exportável:")
    
    st.text_area(
        label="Relatório",
        value=report_text,
        height=265,
        label_visibility="collapsed"
    )
    
    sub1, sub2, sub3, sub4 = st.columns(4)
    cols_sub = [sub1, sub2, sub3, sub4]
    for col, (label, val, status, color) in zip(cols_sub, sub_cards_data):
        with col:
            st.markdown(f"""
            <div class="sub-card">
                <div class="sub-card-label">{label}</div>
                <div class="sub-card-val">{val}</div>
                <div style="font-size:11px; color:{color}; font-weight:600;">{status}</div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.markdown(f"### {metrics_title}")
    st.caption("Atualizado às 10:39:42 BRT")
    
    for title, val, change, color in metrics_list:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-change-positive" style="color: {color};">{change}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# PAINEL DAS 8 CATEGORIAS
st.markdown(f"### 📁 Painel de Análise Integrada das 8 Categorias ({modulo})")
st.caption("Visão detalhada dos setores selecionados no painel lateral:")

active_cats = [c for c in categories if c["active"]]

if active_cats:
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