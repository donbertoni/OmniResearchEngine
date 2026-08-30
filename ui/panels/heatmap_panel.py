import numpy as np
import streamlit as st

from omni.application import liquidity_service
from omni.domain.formatting import fmt_num
from omni.domain.ports import LiquidityDataPort

try:
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


@st.cache_data(ttl=60, show_spinner=False)
def _cached_liquidity_heatmap(modulo: str, base_price: float, _crypto_port, _tradfi_port):
    # Mesmo bug que _cached_dashboard_snapshot (ui/main.py) já corrigiu: sem
    # cache, qualquer interação não relacionada (marcar um checkbox em outro
    # painel) refazia a chamada ao order book da Deribit / volume profile do
    # ES=F. Parâmetros prefixados com "_" não entram na chave de cache -- é
    # assim que o Streamlit lida com argumentos não-hasheáveis como adapters.
    return liquidity_service.get_liquidity_heatmap(modulo, base_price, _crypto_port, _tradfi_port)


def render_heatmap_panel(
    tr: dict,
    modulo: str,
    lang_key: str,
    quotes: dict,
    crypto_liquidity_port: LiquidityDataPort,
    tradfi_liquidity_port: LiquidityDataPort,
) -> None:
    col_sec_title, col_sec_chk = st.columns([4, 1])
    with col_sec_title:
        st.subheader(tr["heatmap_crypto"] if modulo == "Crypto" else tr["heatmap_tradfi"])
    with col_sec_chk:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        st.checkbox(tr["include_report"], value=True, key="chk_include_heatmap")

    if not PLOTLY_AVAILABLE:
        st.warning("⚠️ Plotly module unavailable.")
        return

    default_ticker = "BTC-USD" if modulo == "Crypto" else "ES=F"
    q = quotes.get(default_ticker)
    base_price = q.price if q and q.price else (77000.0 if modulo == "Crypto" else 5000.0)

    liquidity = _cached_liquidity_heatmap(modulo, base_price, crypto_liquidity_port, tradfi_liquidity_port)

    arr_v = np.array(liquidity.volumes, dtype=float)
    max_v = arr_v.max() if len(arr_v) > 0 and arr_v.max() > 0 else 1.0
    color_intensity = np.sqrt(arr_v / max_v) * 100.0

    fig_oi = go.Figure()
    fig_oi.add_trace(
        go.Bar(
            y=liquidity.prices,
            x=liquidity.volumes,
            orientation="h",
            marker=dict(color=color_intensity, colorscale="Jet", showscale=True, colorbar=dict(title="Intensidade", len=0.8, thickness=12, tickfont=dict(color="#C9D1D9"))),
            hoverinfo="text",
            text=[f"Preço: {fmt_num(p)} | Volume: ${v:.2f}{liquidity.unit_label}" for p, v in zip(liquidity.prices, liquidity.volumes)],
            name="Clusters de Liquidez",
        )
    )
    fig_oi.add_hline(
        y=base_price, line_dash="dash", line_color="#58A6FF",
        annotation_text=f"Spot: {fmt_num(base_price)}", annotation_position="bottom right", annotation_font_color="#58A6FF",
    )
    fig_oi.update_layout(
        title="Institutional Liquidity Heatmap" if lang_key == "EN" else "Mapa Térmico de Liquidez Institucional",
        paper_bgcolor="#0B0E14", plot_bgcolor="#161B22", font=dict(color="#C9D1D9", size=12),
        margin=dict(l=20, r=20, t=40, b=20), height=520,
        yaxis=dict(gridcolor="#30363D", title="Price Levels (USD)" if lang_key == "EN" else "Níveis de Preço (USD)"),
        xaxis=dict(gridcolor="#30363D", title="Accumulated Notional Volume" if lang_key == "EN" else "Volume Notional Acumulado"),
    )
    st.plotly_chart(fig_oi, use_container_width=True)
    st.markdown(f"🌐 **API Source:** `{liquidity.source_label}`")
