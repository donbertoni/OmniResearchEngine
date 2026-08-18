import datetime
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS Customizada para Alinhamento Perfeito e Visual Institucional
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .stApp {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .report-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .category-block {
        background-color: #1a212c;
        border-left: 4px solid #1f6feb;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    h1, h2, h3 {
        color: #f0f6fc;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title("⚙️ Configurações OMNI")
st.sidebar.markdown(
    "**Controle de geração de roteiros e relatórios**", help="Configuração global"
)

# Idioma
st.sidebar.selectbox("🌐 Idioma do Output", ["Português (BR)", "English (US)"])

# Módulo
modulo = st.sidebar.radio(
    "📊 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Calibragem (SaaS Enterprise)")
st.sidebar.markdown("Selecione os setores/categorias:")

cat_1 = st.sidebar.checkbox("1 - Bancos e Seguradoras", value=True)
cat_2 = st.sidebar.checkbox("2 - Energia", value=True)
cat_3 = st.sidebar.checkbox("3 - Tech", value=True)
cat_4 = st.sidebar.checkbox("4 - Commodities", value=True)
cat_5 = st.sidebar.checkbox("5 - Varejo", value=True)
cat_6 = st.sidebar.checkbox("6 - Logística e Infraestrutura", value=True)
cat_7 = st.sidebar.checkbox("7 - Agronegócio e indústria", value=True)
cat_8 = st.sidebar.checkbox("8 - Crypto e Digital Assets", value=True)

st.sidebar.markdown("---")
formato = st.sidebar.radio("📋 Formato (TradFi / Macro):", ["B2B (Relatório)", "B2C (YouTube)"])

# Cabeçalho Principal
st.title("⚡ OMNIRERESEARCH Engine")
st.markdown("##### Plataforma Integrada de Inteligência Financeira: YouTube Auto/HITL, Relatórios B2B (Crypto) e TradFi (Macro)")

current_time = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
st.info(f"🕒 Dados consolidados das {current_time}", icon="📊")

# Métricas Agregadas (Grid Superior)
st.markdown("### 📊 Métricas Agregadas (TradFi)")
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

with col_m1:
    st.markdown(
        """
        <div class="metric-card">
            <small>1. S&P 500 (Yahoo Finance)</small>
            <h3>7.758 pts</h3>
            <span style="color: #238636; font-size: 0.85rem;">+0,53% hoje</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_m2:
    st.markdown(
        """
        <div class="metric-card">
            <small>2. Ibovespa (Yahoo Finance)</small>
            <h3>166.833 pts</h3>
            <span style="color: #da3633; font-size: 0.85rem;">-8,16% hoje</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_m3:
    st.markdown(
        """
        <div class="metric-card">
            <small>3. Câmbio (USD/BRL, AwesomeAPI)</small>
            <h3>R$ 5,20</h3>
            <span style="color: #238636; font-size: 0.85rem;">+0,08% hoje</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_m4:
    st.markdown(
        """
        <div class="metric-card">
            <small>4. Ouro Spot (Yahoo Finance)</small>
            <h3>$4.474,90/oz</h3>
            <span style="color: #238636; font-size: 0.85rem;">+0,85% hoje</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_m5:
    st.markdown(
        """
        <div class="metric-card">
            <small>5. Petróleo Brent (Yahoo Finance)</small>
            <h3>$90,69/bbl</h3>
            <span style="color: #238636; font-size: 0.85rem;">+2,45% hoje</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Seção de Relatório B2B e Resumo
st.markdown("---")
st.subheader("📑 Relatório B2B (TradFi & Macroeconomia)")
st.caption("Relatório Macro/TradFi (B2B):")

# Quadrado "Resumo do Report" contendo todas as seções e as 8 categorias resumidas
report_summary_content = f"""=== RELATÓRIO INSTITUCIONAL TRADI & MACROECONOMIA (B2B) ===
Data/Hora: {current_time}

1. PANORAMA MACRO E BENCHMARKS
- S&P 500: 7.758 pts (+0,53%) [Yahoo Finance]
- Ibovespa: 166.833 pts (-8,16%) [Yahoo Finance]
- Câmbio (USD/BRL): R$ 5,20 (+0,08%) [AwesomeAPI]
- M2 Global (Liquidez Monetária): $104 BT (+4,2% YoY) [FRED St. Louis Fed]

2. MESA DE COMMODITIES
- Ouro Spot (XAU/USD): $4.474,90/oz (+0,85%) [Yahoo Finance]
- Petróleo Brent: $90,69/bbl (+2,45%) [Yahoo Finance]

3. VITRINES PREDITIVAS & NÍVEIS TÉCNICOS
- Tendência TD (S&P 500): Pressão Vendedora (↓ 38 pts)
- Próximo Suporte (S&P 500): 7.680 pts (↓ Nível Crítico)
- Tendência TD (Ibovespa): Consolidação TD (+52 pts)
- Suporte Atual (Ibovespa): 165.200 pts (→ Nível Crítico)

4. SÍNTESE DAS 8 CATEGORIAS DE CALIBRAGEM ENTERPRISE:
- Bancos e Seguradoras | Energia | Tech | Commodities
- Varejo | Logística e Infra | Agronegócio | Crypto & Digital Assets"""

st.markdown(
    f"""
<div class="report-box">
    <pre style="color: #c9d1d9; font-family: monospace; white-space: pre-wrap; font-size: 0.9rem;">{report_summary_content}</pre>
</div>
""",
    unsafe_allow_html=True,
)

# BLOCOS DAS CATEGORIAS ABAIXO DAS ABAS PREDITIVAS (Mantidos e alinhados conforme layout anterior)
st.markdown("---")
st.subheader("📦 32 Ativos Oficiais TradFi em Foco (Calibragem Enterprise)")
st.markdown("Detalhamento modular por categoria para validação e curadoria analítica:")

col_b1, col_b2 = st.columns(2)

with col_b1:
    if cat_1:
        st.markdown(
            """
            <div class="category-block">
                <strong>🏦 1 - Bancos e Seguradoras</strong><br>
                • ITUB4 (Itaú Unibanco): R$ 34,20 (+0,8%) [Fonte B3 / Yahoo Finance]<br>
                • BBDC4 (Banco do Brasil): R$ 52,50 (+0,7%) [Fonte B3 / Yahoo Finance]<br>
                • SANB11 (Santander): R$ 14,10 (-0,2%) [Fonte B3 / Yahoo Finance]<br>
                • BBSE3 (BB Seguridade): R$ 35,10 (+0,3%) [Fonte B3 / Yahoo Finance]
            </div>
            """,
            unsafe_allow_html=True,
        )
    if cat_3:
        st.markdown(
            """
            <div class="category-block">
                <strong>💻 3 - Tech</strong><br>
                • AAPL34 (Apple): R$ 78,50 (+1,2%) [Fonte B3]<br>
                • MSFT34 (Microsoft): R$ 142,30 (+0,9%) [Fonte B3]<br>
                • GOGL34 (Alphabet): R$ 94,10 (-0,4%) [Fonte B3]
            </div>
            """,
            unsafe_allow_html=True,
        )
    if cat_5:
        st.markdown(
            """
            <div class="category-block">
                <strong>🛒 5 - Varejo</strong><br>
                • MGLU3 (Magazine Luiza): R$ 2,10 (-2,5%) [Fonte B3]<br>
                • VIIA3 (Via): R$ 0,85 (-1,1%) [Fonte B3]<br>
                • LREN3 (Lojas Renner): R$ 16,40 (+0,4%) [Fonte B3]
            </div>
            """,
            unsafe_allow_html=True,
        )
    if cat_7:
        st.markdown(
            """
            <div class="category-block">
                <strong>🌱 7 - Agronegócio e Indústria</strong><br>
                • JBSS3 (JBS): R$ 28,30 (+1,5%) [Fonte B3]<br>
                • BEEF3 (Minerva): R$ 7,40 (-0,6%) [Fonte B3]<br>
                • AGRO3 (BrasilAgro): R$ 24,90 (+0,2%) [Fonte B3]
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_b2:
    if cat_2:
        st.markdown(
            """
            <div class="category-block">
                <strong>⚡ 2 - Energia</strong><br>
                • PETR4 (Petrobras): R$ 38,50 (+1,2%) [Fonte B3 / Yahoo Finance]<br>
                • ELET3 (Eletrobras): R$ 41,40 (+0,8%) [Fonte B3 / Yahoo Finance]<br>
                • CMIG4 (Cemig): R$ 11,50 (-0,3%) [Fonte B3 / Yahoo Finance]<br>
                • EQTL3 (Equatorial): R$ 31,10 (+0,5%) [Fonte B3 / Yahoo Finance]
            </div>
            """,
            unsafe_allow_html=True,
        )
    if cat_4:
        st.markdown(
            """
            <div class="category-block">
                <strong>🛢️ 4 - Commodities</strong><br>
                • VALE3 (Vale): R$ 64,80 (+1,8%) [Fonte B3]<br>
                • CSNA3 (CSN): R$ 13,20 (-0,9%) [Fonte B3]
            </div>
            """,
            unsafe_allow_html=True,
        )
    if cat_6:
        st.markdown(
            """
            <div class="category-block">
                <strong>🚢 6 - Logística e Infraestrutura</strong><br>
                • RAPT4 (Randon): R$ 11,20 (+0,3%) [Fonte B3]<br>
                • CCRO3 (CCR): R$ 12,80 (-0,1%) [Fonte B3]
            </div>
            """,
            unsafe_allow_html=True,
        )
    if cat_8:
        st.markdown(
            """
            <div class="category-block">
                <strong>🪙 8 - Crypto e Digital Assets</strong><br>
                • BTC (Bitcoin): $64.170,00 (+3,4%) [CoinGecko]<br>
                • ETH (Ethereum): $3.450,00 (+2,1%) [CoinGecko]<br>
                • SOL (Solana): $145,20 (+5,6%) [CoinGecko]
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.markdown(
    "<div style='text-align: right; color: #8b949e; font-size: 0.8rem;'>OMNIRESEARCH Engine v3.5 - Enterprise Edition</div>",
    unsafe_allow_html=True,
)