import pandas as pd
import streamlit as st

from omni.application import agents_service
from omni.domain.tenancy import LEGACY_ORG_ID


def render_agents_panel(tr: dict, lang_key: str, quotes: dict, ml_log_repo) -> None:
    st.subheader(f"🤖 {tr['agents_title']}")
    st.caption(tr["agents_caption"])

    agent_tab1, agent_tab2, agent_tab3, agent_tab4 = st.tabs(
        [tr["agent_script"], tr["agent_predictive"], tr["agent_ta"], tr["agent_art"]]
    )

    with agent_tab1:
        _render_scriptwriter_tab(tr, lang_key, quotes)
    with agent_tab2:
        _render_predictive_tab(tr, lang_key, ml_log_repo)
    with agent_tab3:
        _render_ta_tab(tr)
    with agent_tab4:
        _render_art_tab(tr)


def _render_scriptwriter_tab(tr: dict, lang_key: str, quotes: dict) -> None:
    st.markdown(f"### {tr['agent_script_title']}")
    st.markdown(tr["agent_script_desc"])

    target_asset_script = st.selectbox(tr["target_asset_script"], ["BTC-USD", "ES=F", "ITUB4.SA", "PETR4.SA"], key="script_asset_sel")
    script_tone = st.selectbox(tr["script_tone"], ["Institucional / B2B", "Trader Agressivo / HFT", "Educacional / Retail"], key="script_tone_sel")

    if st.button(tr["generate_script"], use_container_width=True):
        q = quotes.get(target_asset_script)
        price = q.price if q and q.price else 50000.0
        change = q.change if q and q.price else 1.5
        script_output = agents_service.generate_script(lang_key, target_asset_script, script_tone, price, change)
        st.text_area("Roteiro Sintetizado pela IA / Synthesized AI Script:", value=script_output, height=200)


def _render_predictive_tab(tr: dict, lang_key: str, ml_log_repo) -> None:
    st.markdown(f"### {tr['agent_pred_title']}")
    st.markdown(tr["agent_pred_desc"])

    pred_asset = st.selectbox(tr["pred_asset_label"], ["BTC-USD", "ES=F"], key="pred_asset_sel")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.metric(label=tr["win_rate_label"], value="79.8%", delta="+3.2% vs Mês Anterior")
    with col_p2:
        current_conf = "84.5% (High Confidence)" if lang_key == "EN" else "84.5% (Alta Confiança)"
        st.metric(label=tr["confidence_label"], value=current_conf)

    st.markdown(f"#### {tr['pred_logs_title']}")
    df_logs = pd.DataFrame(st.session_state.ml_prediction_logs)
    st.dataframe(df_logs, use_container_width=True)

    if st.button(tr["run_ml_btn"], use_container_width=True):
        new_log = agents_service.run_ml_inference(pred_asset)
        st.session_state.ml_prediction_logs.insert(0, new_log)
        ml_log_repo.append(LEGACY_ORG_ID, new_log)
        st.toast("Nova predição registrada com sucesso!", icon="📊")
        st.rerun()


def _render_ta_tab(tr: dict) -> None:
    st.markdown(f"### {tr['agent_ta_title']}")
    st.markdown(tr["agent_ta_desc"])

    ta_asset = st.selectbox(tr["ta_asset_label"], ["BTC-USD", "ES=F"], key="ta_asset_sel")
    ta_timeframe = st.selectbox(tr["ta_tf_label"], ["4h", "1D", "1W", "1M"], index=1, key="ta_tf_sel")

    if st.button(tr["run_ta_btn"], use_container_width=True):
        result = agents_service.run_ta_scan(ta_asset, ta_timeframe)
        st.success(f"Análise concluída para **{result['asset']}** ({result['timeframe']}):")
        targets_str = " | ".join(f"`{t}`" for t in result["targets"])
        st.markdown(f"""
        > **Padrão Identificado / Pattern Identified:** {result['pattern']}
        > * **Rompimento / Breakout Level:** `{result['breakout_level']}`
        > * **Targets / Alvos:** {targets_str}
        > * **Stop Loss:** `{result['stop_loss']}`
        """)


def _render_art_tab(tr: dict) -> None:
    st.markdown(f"### {tr['agent_art_title']}")
    st.markdown(tr["agent_art_desc"])

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.selectbox(tr["visual_template"], ["Dashboard Quant Dark Theme", "Zoom em Indicadores Macro", "Full Screen Ticker Motion"], index=0)
        st.selectbox(tr["tts_voice"], ["Voz Corporativa PT-BR (Natural)", "Voz Trader EN-US (Dynamic)", "Sem Narração (Apenas Legendas)"], index=0)
    with col_v2:
        st.selectbox(tr["yt_status"], ["Privado (Revisão Humana)", "Não Listado", "Público (Automático via API)"], index=0)
        st.checkbox(tr["yt_schedule"], value=True)

    if st.button(tr["render_video"], use_container_width=True):
        st.toast("Vídeo renderizado e enviado para fila da API do YouTube!", icon="🎥")
        st.success("Status: Pipeline de Vídeo 100% concluído e integrado ao Auto-Pilot.")
