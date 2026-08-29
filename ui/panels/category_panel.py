import streamlit as st

from omni.domain.catalog import get_asset_source
from omni.domain.formatting import fmt_num, fmt_pct


def render_category_panel(tr: dict, modulo: str, active_display_categories: dict, quotes: dict) -> None:
    st.subheader(f"🗂️ {tr['integrated_panel']} ({modulo})")
    selected_categories = list(active_display_categories.keys())
    if not selected_categories:
        return

    cols = st.columns(min(len(selected_categories), 4))
    for idx, cat_name in enumerate(selected_categories):
        cat_info = active_display_categories[cat_name]
        col = cols[idx % len(cols)]
        with col:
            with st.container(border=True):
                cat_key = f"chk_cat_{cat_name}"
                c_title, c_dummy, c_check = st.columns([2.2, 0.8, 0.4], vertical_alignment="center")
                with c_title:
                    st.markdown(
                        f'<div style="font-size: 13px; font-weight: 700; color: #F0F6FC; white-space: nowrap; '
                        f'overflow: hidden; text-overflow: ellipsis;">{cat_name}</div>',
                        unsafe_allow_html=True,
                    )
                with c_dummy:
                    st.empty()
                with c_check:
                    cat_enabled = st.checkbox("", value=st.session_state.get(cat_key, True), key=cat_key, label_visibility="collapsed")

                st.markdown("<div style='border-bottom: 1px solid #30363D; margin-top: 6px; margin-bottom: 6px;'></div>", unsafe_allow_html=True)

                for disp_name, ticker, currency in cat_info["assets"]:
                    q = quotes.get(ticker)
                    price = q.price if q else 0.0
                    change = q.change if q else 0.0
                    asset_key = f"chk_asset_{cat_name}_{ticker}"
                    color_cls = "color-green" if change > 0 else ("color-red" if change < 0 else "color-blue")
                    src_name = get_asset_source(ticker)

                    c_info, c_badge, c_box = st.columns([2.2, 0.8, 0.4], vertical_alignment="center")
                    with c_info:
                        st.markdown(
                            f"""
                            <div style="font-size: 11px;">
                                <div style="color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px;">{disp_name}</div>
                                <div>
                                    <b style="color: #F0F6FC; font-size: 12px;">{currency} {fmt_num(price)}</b>
                                    <span class="{color_cls}" style="font-size: 11px;">({fmt_pct(change)})</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with c_badge:
                        st.markdown(f'<span class="source-badge">{src_name}</span>', unsafe_allow_html=True)
                    with c_box:
                        st.checkbox("", value=st.session_state.get(asset_key, True), key=asset_key, disabled=not cat_enabled, label_visibility="collapsed")

                    st.markdown("<div style='border-bottom: 1px solid #21262D; margin-top: 6px; margin-bottom: 6px;'></div>", unsafe_allow_html=True)
