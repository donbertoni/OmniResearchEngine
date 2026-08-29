CSS_BLOCK = """<style>
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    .status-bar {
        background-color: #131B2A;
        padding: 9px 14px;
        border-radius: 8px;
        border: 1px solid #1E293B;
        color: #94A3B8;
        font-size: 13px;
        height: 42px;
        display: flex;
        align-items: center;
    }
    .warning-bar {
        background-color: #2D2211;
        border: 1px solid #D29922;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #F0F6FC;
        font-size: 13px;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-title { font-size: 11px; color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; justify-content: space-between; }
    .metric-value { font-size: 15px; font-weight: 700; color: #F0F6FC; margin: 2px 0px; }
    .color-green { color: #3FB950 !important; font-weight: 600; }
    .color-red { color: #F85149 !important; font-weight: 600; }
    .color-blue { color: #58A6FF !important; font-weight: 600; }
    .source-badge {
        font-size: 9px;
        color: #8B949E;
        background-color: #21262D;
        border: 1px solid #30363D;
        padding: 1px 4px;
        border-radius: 4px;
        white-space: nowrap;
        display: inline-block;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }
</style>"""


def inject(st) -> None:
    st.markdown(CSS_BLOCK, unsafe_allow_html=True)
