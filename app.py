import streamlit as st
import datetime

# Configuração Inicial da Página
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada (CSS)
st.markdown("""
<style>
    /* Estilização Geral do Container */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Box do Banner Superior */
    .info-banner {
        background-color: #1a2638;
        border: 1px solid #23354d;
        border-radius: 8px;
        padding: 12px 18px;
        font-size: 14px;
        color: #8bb4e7;
        margin-bottom: 20px;
    }

    /* Cards de Métricas Principais */
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
        font-size: 22px;
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

    /* Cards de Resumo Sub-Report */
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
    .sub-card-status {
        font-size: 11px;
        font-weight: 600;
    }

    /* Cards das 8 Categorias no Rodapé */
    .cat-card {
        background-color: #131924;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        height: 100%;
    }
    .cat-title {
        font-size: 15px;
        font-weight: bold;
        color: #38bdf8;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    .cat-item {
        font-size: 12px;
        color: #cbd5e1;
        margin-bottom: 6px;
    }
    .cat-item strong {
        color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR: Configurações & Calibragem
with st.sidebar:
    st.title("⚙️ Configurações OMNI")
    st.caption("Controle de geração de roteiros e relatórios")
    
    st.selectbox("🌐 Idioma do Output:", ["Português (BR)", "English (US)"], index=0)
    
    st.radio("💡 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=0)
    
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
    
    st.radio("🎯 Formato (Crypto):", ["B2B (Relatório)", "B2C (YouTube)"], index=0)
    
    st.info("💡 O modo Auto-Pilot está disponível exclusivamente para entregáveis B2C (YouTube).")

# HEADER PRINCIPAL
st.markdown("# ⚡ OMNIRESEARCH Engine")
st.markdown("**Plataforma Integrada de Inteligência Financeira:** YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

# Banner de horário dos dados
st.markdown("""
<div class="info-banner">
    🕒 <strong>Dados consolidados das 18/08/2026 às 10:39:42 BRT</strong>
</div>
""", unsafe_allow_html=True)

# LAYOUT SUPERIOR (Relatório + Métricas Lado a Lado)
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
        label="Relatório Completo",
        value=report_text,
        height=280,
        label_visibility="collapsed"
    )
    
    # Quadrado/Barra de Resumo abaixo do Report
    sub1, sub2, sub3, sub4 = st.columns(4)
    with sub1:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Tendência 7D (BTC)</div>
            <div class="sub-card-val">Tendência Compradora</div>
            <div class="sub-card-status" style="color: #10b981;">↑ 78 pts</div>
        </div>
        """, unsafe_allow_html=True)
    with sub2:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Próxima Resistência (BTC)</div>
            <div class="sub-card-val">$65.000</div>
            <div class="sub-card-status" style="color: #10b981;">↑ Nível Crítico</div>
        </div>
        """, unsafe_allow_html=True)
    with sub3:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Suporte Crítico (BTC)</div>
            <div class="sub-card-val">$62.500</div>
            <div class="sub-card-status" style="color: #ef4444;">↓ Zona de Defesa</div>
        </div>
        """, unsafe_allow_html=True)
    with sub4:
        st.markdown("""
        <div class="sub-card">
            <div class="sub-card-label">Previsão 48h (BTC)</div>
            <div class="sub-card-val">Alta Moderada</div>
            <div class="sub-card-status" style="color: #38bdf8;">↑ Alvo $65.000</div>
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

# SEÇÃO INFERIOR: BLOCOS DAS 8 CATEGORIAS
st.markdown("### 📂 Painel de Análise Integrada das 8 Categorias")
st.caption("Visão detalhada dos setores selecionados no painel lateral de calibragem:")

# Lista de dados para as 8 categorias
categories = [
    {
        "id": "etf",
        "active": cat_etf,
        "title": "1. ETF's (Spot & Inst.)",
        "items": [
            ("Entrada Líquida (Diária)", "+$248.5M (IBIT / FBTC)"),
            ("AUM Total Spot ETFs", "$58.4 Billion"),
            ("Fluxo Líquido 7D", "+$1.12B (Entrada Ativa)"),
            ("Sentimento Institucional", "Acumulação Forte")
        ]
    },
    {
        "id": "treasury",
        "active": cat_treasury,
        "title": "2. Treasury & Tesourarias",
        "items": [
            ("Holdings MicroStrategy", "226.500 BTC"),
            ("Compras Corporativas 7D", "+$12.4M agregados"),
            ("Dominância Corporativa", "3,15% do Circulante"),
            ("Empresas Públicas em BTC", "42 Empresas")
        ]
    },
    {
        "id": "mineracao",
        "active": cat_mineracao,
        "title": "3. Mineração & Hashrate",
        "items": [
            ("Hashrate Agregado", "642 EH/s (+1.4%)"),
            ("Hashprice (TH/dia)", "$0,048 USD"),
            ("Dificuldade Atual", "86.8 T (Próx +1.8%)"),
            ("Estresse dos Mineradores", "Médio / Neutro")
        ]
    },
    {
        "id": "spot",
        "active": cat_spot,
        "title": "4. Volume Spot (24 hs)",
        "items": [
            ("Volume Global Spot", "$28.4 Billion (+14.2%)"),
            ("Binance Share", "44.8% ($12.7B)"),
            ("Dominância Par BTC/USDT", "58.2% do Volume"),
            ("Profundidade de Livro (2%)", "$310M no Bid/Ask")
        ]
    },
    {
        "id": "futuros",
        "active": cat_futuros,
        "title": "5. Volume Futuros (24 hs)",
        "items": [
            ("Volume Derivados 24h", "$89.2 Billion"),
            ("Razão Volume/Spot", "3.14x (Alavancagem Controlada)"),
            ("Proporção Long/Short", "52.4% Longs"),
            ("Volume de Liquidações 24h", "$42.1M (Pred. Shorts)")
        ]
    },
    {
        "id": "oi",
        "active": cat_oi,
        "title": "6. Open Interest (OI)",
        "items": [
            ("Open Interest BTC", "$32.1 Billion (+3.8%)"),
            ("CME Open Interest", "$9.8B (30.5% Mkt Share)"),
            ("Funding Rate Médio", "+0.0092% (Neutro)"),
            ("Alavancagem Estática", "Moderada / Segura")
        ]
    },
    {
        "id": "defi",
        "active": cat_defi,
        "title": "7. DeFi & Layer 1s",
        "items": [
            ("TVL Agregado DeFi", "$84.2 Billion (+2.4%)"),
            ("Liderança TVL", "Ethereum ($48.2B / 57.2%)"),
            ("Solana DEX Volume 24h", "$1.82 Billion"),
            ("Gas Médio Ethereum", "12 Gwei (Baixo)")
        ]
    },
    {
        "id": "stablecoins",
        "active": cat_stable,
        "title": "8. Stablecoins & Liquidez",
        "items": [
            ("Market Cap Stables", "$168.4 Billion (+0.8%)"),
            ("Dominância USDT", "69.2% ($116.5B)"),
            ("Net Inflow Corretoras", "+$412M (Poder de Compra)"),
            ("Oferta Liquida em Exchanges", "$24.8B Prontos")
        ]
    }
]

# Renderização dos 8 blocos em Grid (4 Colunas x 2 Linhas)
active_categories = [c for c in categories if c["active"]]

if active_categories:
    # Dividir as categorias ativas em grupos de 4 por linha
    for row_idx in range(0, len(active_categories), 4):
        cols = st.columns(4)
        row_cats = active_categories[row_idx:row_idx+4]
        
        for col, cat in zip(cols, row_cats):
            with col:
                items_html = "".join([
                    f'<div class="cat-item">• {k}: <strong>{v}</strong></div>'
                    for k, v in cat["items"]
                ])
                
                st.markdown(f"""
                <div class="cat-card">
                    <div class="cat-title">{cat["title"]}</div>
                    {items_html}
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("Nenhuma categoria selecionada no painel de calibragem da barra lateral.")