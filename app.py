import streamlit as st
from datetime import datetime

# 1. Configuração da página
st.set_page_config(
    page_title="OmniResearch Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Captura de horário
snapshot_time = datetime.now().strftime("%d/%m/%Y às %H:%M BRT")
snapshot_hour = datetime.now().strftime("%H:%M BRT")

# 3. Estilização CSS (Ultra-Alto Contraste)
st.markdown("""
<style>
    .stApp { 
        background-color: #080D1A; 
        color: #FFFFFF; 
    }
    
    div[data-testid="stMetric"] { 
        background-color: #0F172A !important; 
        padding: 10px 14px !important; 
        border-radius: 8px !important; 
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 4px !important;
    }
    
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricLabel"] div,
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span {
        color: #FFFFFF !important;
        background: transparent !important;
        font-size: 0.90rem !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] *,
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] span,
    [data-testid="stMetricValue"] p {
        color: #FFFFFF !important;
        background: transparent !important;
        font-size: 1.20rem !important;
        font-weight: 800 !important;
        opacity: 1 !important;
        white-space: nowrap !important;
    }

    [data-testid="stMetricDelta"],
    [data-testid="stMetricDelta"] *,
    [data-testid="stMetricDelta"] div,
    [data-testid="stMetricDelta"] span {
        background: transparent !important;
    }

    label, label p, [data-testid="stWidgetLabel"] p, .stCaption, .stCaption p {
        color: #F8FAFC !important;
        font-size: 0.90rem !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    .timestamp-badge {
        background-color: #0F172A;
        color: #38BDF8;
        border: 1px solid #0284C7;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 4px;
    }

    .stTextArea textarea {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        font-size: 1.00rem !important;
        line-height: 1.5 !important;
        font-family: 'Inter', sans-serif !important;
    }

    div[data-testid="stColumn"] button {
         border-radius: 8px !important;
         font-weight: 700 !important;
    }
    
    button[kind="primary"] {
        background-color: #2563EB !important;
        border: none !important;
        color: #FFFFFF !important;
    }
    
    h1, h2, h3 { 
        color: #FFFFFF !important; 
        font-weight: 700 !important; 
    }
</style>
""", unsafe_allow_html=True)

# 4. Cabeçalho
col_logo, col_target, col_mode = st.columns([2, 2, 1.2])

with col_logo:
    st.title("⚡ OMNIRESEARCH")
    st.caption("Engine de Inteligência Financeira Multiativo")
    st.markdown(f'<div class="timestamp-badge">🕒 Report Gerado em: {snapshot_time}</div>', unsafe_allow_html=True)

with col_target:
    target_profile = st.selectbox(
        "🎯 Perfil do Relatório (Target):",
        ["🎥 B2C: YouTube Crypto Content", "💼 B2B: Briefing Institucional (Escritórios/Wealth)"]
    )

with col_mode:
    autopilot_mode = st.toggle("Modo Autopilot", value=False)
    st.caption("Autopilot ON: Publicação automática sem HITL.")

st.divider()

# 5. Layout Principal
col_main, col_sidebar = st.columns([2.1, 1.1])

if "🎥 B2C" in target_profile:
    with col_main:
        st.subheader("📄 Painel de Aprovação de Roteiro - YouTube (HITL)")
        
        tab_pt, tab_en = st.tabs(["🇧🇷 PT-BR (Crypto & Liquidez Global)", "🇺🇸 EN-US (Crypto & Global Liquidity)"])
        
        with tab_pt:
            roteiro_pt = st.text_area(
                "Roteiro Estendido LLM (~2 min 30 seg de tela):",
                value=f"""[00:00 - HOOK DE RETENÇÃO]
(Horário de criação do Report: {snapshot_time})
O Fear & Greed Index marca 68 pontos em ganância moderada enquanto o Bitcoin sustenta a faixa dos $94,500. Porém, o verdadeiro gatilho estrutural vem do M2 Global, que atingiu nova máxima histórica em $104.8 Trilhões.

[00:35 - BITCOIN & DOMINÂNCIA]
Com a dominância do Bitcoin recuando para 57.8%, vemos os primeiros sinais claros de rotação de liquidez para as principais Layer 1s do mercado. O Funding Rate zerado em 0.0100% mostra alavancagem saudável e sem sinais de euforia desmedida no mercado derivativo.

[01:10 - ALTCOINS LÍDERES: ETHEREUM E SOLANA]
O Ethereum testa $3,420 empurrado por novos fluxos institucionais nos ETFs spot, enquanto Solana dispara para $188.40 impulsionada pelo volume recorde nas DEXs da rede.

[01:45 - ANÁLISE TÉCNICA E MATRIZ PREDITIVA]
A zona de suporte imediata do BTC reside em $93.8k, com resistência crítica mapeada em $97.2k. Nossa matriz preditiva aponta 65% de probabilidade autista para as próximas 48 horas.

[02:15 - ENCERRAMENTO E DISCLAIMER]
Gerencie seu risco e defina seus stops. Conteúdo exclusivamente educativo.""",
                height=480
            )
        
        with tab_en:
            roteiro_en = st.text_area(
                "Extended Script (~2 min 30 sec):",
                value=f"""[00:00 - HOOK]
(Report Creation Time: {snapshot_time})
Fear & Greed Index at 68 as Bitcoin holds $94,500. Global M2 expansion to $104.8T remains the macro catalyst.

[00:35 - BTC DOMINANCE & ROTATION]
BTC Dominance dipping to 57.8% signals active capital rotation toward high-beta Layer-1s. Funding Rate neutral at 0.0100%.

[01:10 - ETH & SOL]
ETH pushes past $3,420 backed by ETF inflows, while Solana rallies to $188.40 on record DEX volumes.

[01:45 - TECHNICAL LEVELS]
Key BTC support stands at $93.8k and resistance at $97.2k. Predictive matrix flags a 65% bullish probability over 48h.

[02:15 - CLOSING]
Manage your downside risk. Educational content only.""",
                height=480
            )

        st.subheader("🎯 Níveis Chave & Matriz Preditiva")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Zona de Suporte", "$93.8k - $94.2k", "Forte Defesa")
        m2.metric("Zona de Resistência", "$97.2k - $98.5k", "Alvo Chave")
        m3.metric("Matriz Preditiva 48h", "65% Bullish", "Alta Confiança")
        m4.metric("M2 Total Supply", "$104.8T", "+4.2% YoY")

    with col_sidebar:
        st.subheader("📊 Ingestão de Mercado (Crypto)")
        st.caption(f"🕒 Horário de criação do Report: {snapshot_hour}")
        
        st.metric("1. Fear & Greed Index", "68 (Greed)", "+3 pts")
        st.metric("2. BTC / USDT", "$94,500.00", "+1.25%")
        st.metric("3. BTC Dominance", "57.8%", "-0.4% (Rotação)")
        st.metric("4. ETH / USDT", "$3,420.50", "+1.85%")
        st.metric("5. SOL / USDT", "$188.40", "+4.12%")
        st.metric("6. BTC Funding Rate", "0.0100%", "Neutro (Saudável)")
        
        st.subheader("🛡️ NLP Guardrails (YT/CVM)")
        st.markdown("* **Clickbait Control:** ✅ Aprovado\n* **Disclaimer de Risco:** ✅ Presente\n* **Análise L1s / Price Action:** ✅ Válido")

else:
    with col_main:
        st.subheader("📄 Briefing Matinal Institucional (B2B)")
        st.text_area("Relatório Estruturado Private:", value=f"Conteúdo B2B Macro & TradFi (Criado em {snapshot_time})...", height=480)
        
        st.subheader("🎯 Indicadores Macro Chave")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Taxa Selic", "10.50%", "Estável")
        m2.metric("Fed Funds", "5.25%", "Estável")
        m3.metric("DI1F27", "11.15%", "-4 bps")
        m4.metric("M2 Global", "$104.8T", "+4.2% YoY")

    with col_sidebar:
        st.subheader("📊 Ingestão TradFi & Macro")
        st.caption(f"🕒 Horário de criação do Report: {snapshot_hour}")
        st.metric("1. Ibovespa Futuros", "128,500", "+0.35%")
        st.metric("2. S&P 500 Futures", "5,840.50", "+0.40%")
        st.metric("3. Dólar / Real", "R$ 5.48", "-0.22%")
        st.metric("4. Petróleo Brent", "$78.20/bbl", "+0.12%")
        
        st.subheader("🛡️ Compliance & Risk")
        st.markdown("* **Suitability Check:** ✅ Adequado\n* **Divulgação CVM 598:** ✅ Em conformidade\n* **Projeções de Mercado:** ✅ Auditadas")

st.divider()

# 6. Botões de Ação
btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
with btn_col1:
    if st.button("🚀 APROVAR E DISPARAR DISTRIBUIÇÃO", type="primary", use_container_width=True):
        st.success(f"Aprovado! Disparando pipeline para: {target_profile}")
with btn_col2:
    if st.button("🔄 REGERAR PROMPT", use_container_width=True):
        st.warning("Solicitando nova versão para a LLM...")
with btn_col3:
    if st.button("💾 SALVAR NO SUPABASE", use_container_width=True):
        st.info("Rascunho registrado no banco de dados!") 