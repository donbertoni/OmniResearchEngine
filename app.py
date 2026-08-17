import streamlit as st
from datetime import datetime

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

# Dados Mockados / Estado Atual (17/08/2026 14:44:16 BRT)
data_atual = "17/08/2026 às 14:44:16 BRT"

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
    "🎯 Formato (TradFi (Macro)):",
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

with col_left:
    st.subheader("📰 Relatório B2B (TradFi & Macroeconomia)")
    st.caption("Relatório Macro/TradFi (B2B):")
    
    # Texto do Relatório B2B com padrão corrigido (Ibovespa com pontuação completa no item 3)
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

3. VETORES PREDITIVOS E TENDÊNCIAS
- S&P 500 (EUA): Tendência 7D (Pressão Vendedora (38 pts)) | Matriz Preditiva 48h: Consolidação (-> Sem Viés Claro (46 pts))
- Ibovespa (Brasil): Tendência 7D (Consolidação 7D (52 pts)) | Matriz Preditiva 48h: Consolidação (-> Sem Viés Claro (49 pts))"""

    st.text_area("", value=relatorio_texto, height=310, disabled=False)
    
    # Cards de Vetores Preditivos e Tendências
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown("""
        <div class="stCard">
            <div class="metric-label">Tendência 7D (S&P 500)</div>
            <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">Pressão Vendedora</div>
            <div class="status-red">↓ Teste de Suporte (38 pts)</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="stCard">
            <div class="metric-label">Tendência 7D (Ibovespa)</div>
            <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">Consolidação 7D</div>
            <div class="status-blue">→ Defesa de Nível (52 pts)</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="stCard">
            <div class="metric-label">Preditiva 48h (S&P 500)</div>
            <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">Consolidação</div>
            <div class="status-blue">→ Sem Viés Claro (46 pts)</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="stCard">
            <div class="metric-label">Preditiva 48h (Ibovespa)</div>
            <div style="font-size: 16px; font-weight: bold; color: #f8fafc;">Consolidação</div>
            <div class="status-blue">→ Sem Viés Claro (49 pts)</div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.subheader("📊 Métricas Agregadas")
    st.caption(f"Atualizado às {data_atual.split('às ')[1] if 'às ' in data_atual else data_atual}")
    
    # Métricas da Direita
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