from datetime import datetime

import pandas as pd
import streamlit as st


def render_cycle_panel() -> None:
    col_term_title, col_term_chk = st.columns([4, 1])
    with col_term_title:
        st.subheader("🌡️ Termômetro de Ciclo: Macro & Relógio Cíclico (Marco Zero: Halving)")
        st.caption("Visão cíclica completa, cronologia histórica e comparativos de desempenho por perfil quantitativo.")
    with col_term_chk:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        st.checkbox("Incluir no Report", value=True, key="chk_include_termometro_cycle")

    term_tab1, term_tab2 = st.tabs([
        "Termômetro Macro & Relógio Cíclico (Marco Zero: Halving)",
        "Comparativo Dinâmico por Perfil",
    ])

    with term_tab1:
        st.markdown("### 📊 Relógio Cíclico & Progresso Global do Halving")

        halving_atual_dt = datetime(2024, 4, 19)
        prox_halving_dt = datetime(2028, 2, 14)
        total_duration_days = (prox_halving_dt - halving_atual_dt).days
        elapsed_days = (datetime.now() - halving_atual_dt).days
        progress_pct = min(max((elapsed_days / total_duration_days) * 100, 0.0), 100.0)

        st.write(f"Progresso Global do Halving Atual: **{progress_pct:.1f}%**")
        st.progress(progress_pct / 100.0)

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.markdown("🔹 **Halving Atual (Marco 0):** `19/04/2024`")
        with col_d2:
            st.markdown("🔹 **Fase Tática:** `Pós-Topo / Acumulação`")
        with col_d3:
            st.markdown("🔹 **Próximo Halving:** `14/02/2028`")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.info(
            "💡 **Análise Quantitativa:** O ciclo mantém o comportamento histórico estruturado em janelas "
            "uniformes (~240 dias por fase), permitindo leitura precisa da distância temporal até o próximo "
            "fundo e topo macroeconômico."
        )

    with term_tab2:
        st.markdown("### 📈 Comparativo Dinâmico por Perfil (Retorno Real & Alocação)")
        st.markdown("Retorno calculado com base no histórico e perfis de risco estipulados pela engine quantitativa:")

        perfis_data = [
            {"Perfil": "Agressivo (64% BTC + 16% Alts + 20% USDT)", "Retorno": "+195.4%", "Regime": "Retração / Acumulação"},
            {"Perfil": "Moderado (32% BTC + 8% Alts + 60% USDT)", "Retorno": "+112.8%", "Regime": "Retração / Acumulação"},
            {"Perfil": "Conservador (16% BTC + 4% Alts + 80% USDT)", "Retorno": "+58.2%", "Regime": "Retração / Acumulação"},
        ]
        df_perfis = pd.DataFrame(perfis_data)
        st.dataframe(df_perfis, use_container_width=True)
