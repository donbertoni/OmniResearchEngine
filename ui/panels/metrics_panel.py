import streamlit as st

from omni.domain.catalog import get_benchmark_source
from omni.domain.formatting import fmt_num, fmt_pct
from omni.domain.models import GlobalCryptoStats, MarketSentiment


def render_metrics_panel(tr: dict, modulo: str, active_benchmarks: list, quotes: dict, sentiment: MarketSentiment, global_stats: GlobalCryptoStats) -> None:
    st.subheader(f"📊 {tr['metrics']} ({modulo})")
    st.caption("Updated | Source: Official APIs")

    for item in active_benchmarks:
        label = item["label"]
        val_str, chg_str, change_cls = "0", "0%", "color-blue"
        src_badge = f'<span class="source-badge">{get_benchmark_source(item)}</span>'

        if item.get("type") == "fng_api":
            val_str = sentiment.value
            cls_map = {"Greed": "color-green", "Neutral": "color-blue", "Fear": "color-red"}
            change_cls = cls_map.get(sentiment.classification, "color-blue")
            chg_str = f"Sentiment: {sentiment.classification}"
        elif item.get("type") == "global_api":
            sub_k = item.get("sub_key")
            val_str = global_stats.btc_dominance_display if sub_k == "btc_d" else global_stats.usdt_dominance_display
            chg_val = global_stats.btc_dominance_change if sub_k == "btc_d" else global_stats.usdt_dominance_change
            chg_str = fmt_pct(chg_val)
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")
        elif item.get("ticker"):
            q = quotes.get(item["ticker"])
            price = q.price if q else 0.0
            chg_val = q.change if q else 0.0
            val_str = f"{item.get('prefix', '')}{fmt_num(price)}"
            chg_str = fmt_pct(chg_val)
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")

        st.markdown(
            f'<div class="metric-card"><div class="metric-title"><span>{label}</span> {src_badge}</div>'
            f'<div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>',
            unsafe_allow_html=True,
        )
