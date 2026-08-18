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
        cat_1 = st.checkbox("1 - Índices Globais", value=True)
        cat_2 = st.checkbox("2 - Curva de Juros & Yields", value=True)
        cat_3 = st.checkbox("3 - Commodities", value=True)
        cat_4 = st.checkbox("4 - Câmbio & FX", value=True)
        cat_5 = st.checkbox("5 - Renda Fixa & Crédito", value=True)
        cat_6 = st.checkbox("6 - Indicadores Econômicos", value=True)
        cat_7 = st.checkbox("7 - Real Estate & REITs", value=True)
        cat_8 = st.checkbox("8 - Volatilidade & Riscos (VIX)", value=True)
    
    st.divider()
    
    formato_label = f"🎯 Formato ({modulo}):"
    formato = st.radio(formato_label, ["B2B (Relatório)", "B2C (YouTube)"], index=0)
    
    st.subheader("🤖 Automação & Auto-Pilot")
    auto_pilot = st.toggle("Ativar Modo Auto-Pilot", value=(formato == "B2C (YouTube)"))
    
    if auto_pilot:
        st.markdown(f"""
        <div class="autopilot-box">
            ⚡ <strong>Auto-Pilot Ativo ({modulo})</strong><br/>
            Pipeline automático executando coleta de dados, síntese B2B e geração de roteiros/vídeos.
        </div>
        """, unsafe_allow_html=True)
        freq_auto = st.select_slider("Frequência de disparo:", options=["1h", "4h", "12h", "24h"], value="4h")
    else:
        st.info("✋ Modo Manual / Human-In-The-Loop (HITL) selecionado.")

# ÁREA PRINCIPAL DA DASHBOARD
st.markdown("# ⚡ OMNIRESEARCH Engine")
st.markdown("**Plataforma Integrada de Inteligência Financeira:** YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

# Banner de Status da Atualização
st.markdown(f"""
<div class="info-banner">
    🕒 <strong>Dados consolidados das 18/08/2026 às 10:39:42 BRT</strong> &nbsp;|&nbsp; 
    Status da API: <span style="color:#10b981;">● Online</span> &nbsp;|&nbsp; 
    Módulo Ativo: <strong>{modulo}</strong>
</div>
""", unsafe_allow_html=True)

# LÓGICA DE DADOS DINÂMICOS (CRYPTO vs TRADFI)
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
        {
            "active": cat_1,
            "title": "1. ETF's (Spot & Inst.)",
            "badge": "Institutional",
            "data": [("Entrada Líquida Diária", "+$248.5M"), ("AUM Total Spot ETFs", "$58.4B"), ("Atividade IBIT / FBTC", "Acumulação Alta"), ("Fluxo Líquido (7D)", "+$1.12B")]
        },
        {
            "active": cat_2,
            "title": "2. Treasury & Tesourarias",
            "badge": "Corporate",
            "data": [("MicroStrategy Holdings", "226.500 BTC"), ("Compras 7D Corporativo", "+$12.4M"), ("Dominância no Circulante", "3,15%"), ("Reservas em Balanço", "Estáveis")]
        },
        {
            "active": cat_3,
            "title": "3. Mineração & Hashrate",
            "badge": "On-Chain",
            "data": [("Hashrate Agregado", "642 EH/s"), ("Hashprice (TH/dia)", "$0,048 USD"), ("Dificuldade Atual", "86.8 T"), ("Estresse Mineradores", "Neutro")]
        },
        {
            "active": cat_4,
            "title": "4. Volume Spot (24 hs)",
            "badge": "Market Data",
            "data": [("BTC / USDT Spot Price", "$64.481,00"), ("ETH / USDT Spot Price", "$1.909,21"), ("SOL / USDT Spot Price", "$76,05"), ("Volume Global 24h", "$28.4B")]
        },
        {
            "active": cat_5,
            "title": "5. Volume Futuros (24 hs)",
            "badge": "Derivatives",
            "data": [("Volume Derivados 24h", "$89.2B"), ("Funding Rate BTC", "+0.012%"), ("Viés de Financiamento", "Neutro/Comprador"), ("Proporção Longs", "52,4%")]
        },
        {
            "active": cat_6,
            "title": "6. Open Interest (OI)",
            "badge": "Derivatives",
            "data": [("Open Interest Total", "$32.1B"), ("CME Market Share", "30,5% ($9.8B)"), ("Nível de Alavancagem", "Moderado"), ("Risco de Liquidação", "Baixo")]
        },
        {
            "active": cat_7,
            "title": "7. DeFi & Layer 1s",
            "badge": "Ecosystem",
            "data": [("Dominância Bitcoin", "56,56% (+0,63%)"), ("TVL Agregado DeFi", "$84.2B"), ("Solana DEX Volume", "$1.82B"), ("Taxa Gas Ethereum", "12 Gwei")]
        },
        {
            "active": cat_8,
            "title": "8. Stablecoins & Liquidez",
            "badge": "Liquidity",
            "data": [("Reservas Corretoras", "2.05M BTC"), ("Tendência de Reservas", "Outflow Contínuo"), ("Fear & Greed Index", "41 / 100 (Medo)"), ("Poder de Compra USDT", "Elevado")]
        }
    ]

else:  # TRADFI (MACRO)
    report_title = "📄 Relatório B2B (TradFi & Macro)"
    metrics_title = "📊 Métricas Agregadas (TradFi & Macro)"
    
    report_text = """=== RELATÓRIO INSTITUCIONAL TRADFI & MACRO (B2B) ===
Data/Hora: 18/08/2026 às 10:39:42 BRT

1. MACROECONOMIA & BENCHMARKS GLOBAIS
- S&P 500 (SPX): 5.580,20 (+0,45%) (S&P Global)
- Nasdaq 100 (NDX): 19.820,10 (+0,62%) (Nasdaq)
- DXY (Índice Dólar): 102,40 (-0,18%) (ICE)
- US10Y (Treasury 10 anos): 3,85% (-4 bps) (US Treasury)
- Ouro Spot (XAU/USD): $2.450,00/oz (+0,80%) (COMEX)

2. JUROS, POLÍTICA MONETÁRIA & BRASIL
- Fed Funds Rate: 5,25% - 5,50% (Pausa Monit.) (FOMC)
- Selic (Brasil): 10,50% a.a. (Copom)
- Inflação IPCA (12M): 4,12% (IBGE)
- USD / BRL: R$ 5,42 (-0,32%) (B3)

3. VETORES PREDITIVOS E NÍVEIS TÉCNICOS (S&P 500)
- Tendência Macro 7D: Tendência Altista (82 pts)"""

    sub_cards_data = [
        ("Tendência Macro (SPX)", "Altista", "↑ 82 pts", "#10b981"),
        ("Resistência (SPX)", "5.620 pts", "↑ Nível Crítico", "#10b981"),
        ("Suporte Crítico", "5.500 pts", "↓ Zona Defesa", "#ef4444"),
        ("Previsão 48h", "Alta Moderada", "↑ Alvo 5.600", "#38bdf8")
    ]

    metrics_list = [
        ("1. S&P 500 Index (SPX)", "5.580,20", "+0,45% hoje", "#10b981"),
        ("2. Nasdaq 100 (NDX)", "19.820,10", "+0,62% hoje", "#10b981"),
        ("3. DXY Dollar Index", "102,40", "-0,18% hoje", "#ef4444"),
        ("4. US 10Y Yield (Treasury)", "3,85%", "-4 bps hoje", "#10b981"),
        ("5. Ouro Spot (XAU/USD)", "$2.450,00", "+0,80% hoje", "#10b981")
    ]

    categories = [
        {
            "active": cat_1,
            "title": "1. Índices Globais",
            "badge": "Equity",
            "data": [("S&P 500", "5.580,20 (+0.45%)"), ("Nasdaq 100", "19.820,10 (+0.62%)"), ("IBOVESPA", "128.450 (+0.35%)"), ("Euro Stoxx 50", "4.890,10 (+0.12%)")]
        },
        {
            "active": cat_2,
            "title": "2. Curva de Juros & Yields",
            "badge": "Rates",
            "data": [("US 10Y Treasury", "3,85% (-4bps)"), ("US 02Y Treasury", "4,05% (-2bps)"), ("Fed Funds Rate", "5.25% - 5.50%"), ("DI1 Jan 2027 (BR)", "10.85%")]
        },
        {
            "active": cat_3,
            "title": "3. Commodities",
            "badge": "Real Assets",
            "data": [("Ouro Spot (XAU)", "$2.450,00/oz"), ("Petróleo BRENT", "$78,50/bbl"), ("Minério de Ferro", "$102,40/ton"), ("Soja (CBOT)", "$1.015,00/bu")]
        },
        {
            "active": cat_4,
            "title": "4. Câmbio & FX",
            "badge": "Currencies",
            "data": [("DXY Index", "102,40 (-0.18%)"), ("USD / BRL", "R$ 5,42 (-0.32%)"), ("EUR / USD", "1.0920 (+0.15%)"), ("GBP / USD", "1.2850 (+0.22%)")]
        },
        {
            "active": cat_5,
            "title": "5. Renda Fixa & Crédito",
            "badge": "Credit",
            "data": [("US High Yield Spread", "320 bps"), ("Corporate Investment Grade", "110 bps"), ("Selic Metá", "10,50% a.a."), ("Inflação Implicita BR", "5,45%")]
        },
        {
            "active": cat_6,
            "title": "6. Indicadores Econômicos",
            "badge": "Macro Data",
            "data": [("US CPI (YoY)", "2.9%"), ("US Payroll (Mensal)", "+114K Jobs"), ("IPCA Brasil (12M)", "4,12%"), ("PIB EUA (QoQ Est.)", "2.8%")]
        },
        {
            "active": cat_7,
            "title": "7. Real Estate & REITs",
            "badge": "Real Estate",
            "data": [("Vanguard REIT (VNQ)", "$88,40 (+0.5%)"), ("IFIX (Fundos Imob.)", "3.380 pts (+0.1%)"), ("Taxa Hipoteca US 30Y", "6.48%"), ("Vacância Comercial SP", "18.2%")]
        },
        {
            "active": cat_8,
            "title": "8. Volatilidade & Riscos",
            "badge": "Risk / Vol",
            "data": [("VIX Index (S&P 500)", "15.20 (-0.85)"), ("MOVE Index (Treasuries)", "98.40"), ("Risco País Brasil (CDS 5Y)", "162 bps"), ("Sentimento do Mercado", "Apetite ao Risco")]
        }
    ]

# RENDERIZAÇÃO DA DASHBOARD SUPERIOR (Relatório + Métricas)
col_left, col_right = st.columns([1.65, 1], gap="medium")

with col_left:
    st.markdown(f"### {report_title}")
    st.caption(f"Relatório {modulo} com indicadores integrados ao exportável:")
    
    st.text_area(
        label="Relatório",
        value=report_text,
        height=265,
        label_visibility="collapsed"
    )
    
    # Quadrado/Barra de Resumo abaixo do Report
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

# RENDERIZAÇÃO DA SEÇÃO INFERIOR: PAINEL DAS 8 CATEGORIAS
st.markdown(f"### 📁 Painel de Análise Integrada das 8 Categorias ({modulo})")
st.caption("Métricas detalhadas e consolidadas diretamente com os dados do relatório acima:")

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