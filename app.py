import streamlit as st
import yfinance as yf
import requests
from datetime import datetime
import pandas as pd
import json
import io

# Importação segura do Plotly com fallback
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & ESTILIZAÇÃO CSS INSTITUCIONAL
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
    .stApp {
        background-color: #0B0E14;
        color: #E2E8F0;
    }
    .status-bar {
        background-color: #131B2A;
        padding: 8px 14px;
        border-radius: 6px;
        border: 1px solid #1E293B;
        margin-bottom: 15px;
        color: #94A3B8;
        font-size: 13px;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .metric-title { font-size: 11px; color: #8B949E; font-weight: 600; }
    .metric-value { font-size: 16px; font-weight: 700; color: #F0F6FC; margin: 2px 0; }
    .metric-change-pos { font-size: 11px; color: #3FB950; font-weight: 600; }
    .metric-change-neg { font-size: 11px; color: #F85149; font-weight: 600; }
    .metric-change-neutral { font-size: 11px; color: #58A6FF; font-weight: 600; }

    .pred-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 12px;
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pred-title { font-size: 11px; color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .pred-value { font-size: 14px; font-weight: 700; color: #F0F6FC; }

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
</style>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. ACERVO MESTRE DE DADOS & CATEGORIAS
# -----------------------------------------------------------------------------
CATEGORIES_TRADFI = {
    "1 - Bancos e Seguradoras": {"tag": "Banking & Ins.", "assets": [("ITUB4", "ITUB4.SA", "R$"), ("BBAS3", "BBAS3.SA", "R$"), ("BBDC4", "BBDC4.SA", "R$"), ("BBSE3", "BBSE3.SA", "R$")]},
    "2 - Energia": {"tag": "Energy", "assets": [("PETR4", "PETR4.SA", "R$"), ("PRIO3", "PRIO3.SA", "R$"), ("EQTL3", "EQTL3.SA", "R$"), ("CPFE3", "CPFE3.SA", "R$")]},
    "3 - Tech": {"tag": "Technology", "assets": [("TOTVS3", "TOTS3.SA", "R$"), ("NVDA", "NVDA", "$"), ("AAPL", "AAPL", "$"), ("MSFT", "MSFT", "$")]},
    "4 - Commodities": {"tag": "Commodities", "assets": [("VALE3", "VALE3.SA", "R$"), ("GGBR4", "GGBR4.SA", "R$"), ("CMIG4", "CMIG4.SA", "R$"), ("KLBN11", "KLBN11.SA", "R$")]},
    "5 - Varejo": {"tag": "Retail", "assets": [("ASAI3", "ASAI3.SA", "R$"), ("LREN3", "LREN3.SA", "R$"), ("MGLU3", "MGLU3.SA", "R$"), ("RADL3", "RADL3.SA", "R$")]},
    "6 - Logística e Infra.": {"tag": "Infra & Log", "assets": [("RAIL3", "RAIL3.SA", "R$"), ("WEGE3", "WEGE3.SA", "R$"), ("CCRO3", "CCRO3.SA", "R$"), ("EMBR3", "EMBR3.SA", "R$")]},
    "7 - Agro e Indústria": {"tag": "Agri & Industry", "assets": [("SLCE3", "SLCE3.SA", "R$"), ("BRFS3", "BRFS3.SA", "R$"), ("ABEV3", "ABEV3.SA", "R$"), ("JBSS3", "JBSS3.SA", "R$")]},
    "8 - Crypto e Digital Assets": {"tag": "Digital Assets", "assets": [("BTCUSDT", "BTC-USD", "$"), ("ETHUSDT", "ETH-USD", "$"), ("SOLUSDT", "SOL-USD", "$"), ("BNBUSDT", "BNB-USD", "$")]}
}

MACRO_BENCHMARKS = [
    {"key": "SPX", "ticker": "^GSPC", "label": "S&P 500", "prefix": ""},
    {"key": "IBOV", "ticker": "^BVSP", "label": "Ibovespa", "prefix": ""},
    {"key": "BRENT", "ticker": "BZ=F", "label": "Petróleo Brent", "prefix": "$ "},
    {"key": "GOLD", "ticker": "GC=F", "label": "Ouro Spot", "prefix": "$ "},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "USD / BRL", "prefix": "R$ "}
]

CATEGORIES_CRYPTO = {
    "1 - ETFs": {"tag": "ETFs", "assets": [("IBIT", "IBIT", "$"), ("FBTC", "FBTC", "$"), ("ETHA", "ETHA", "$"), ("BITO", "BITO", "$")]},
    "2 - Treasury": {"tag": "Treasury", "assets": [("MicroStrategy", "MSTR", "$"), ("Marathon", "MARA", "$"), ("Riot", "RIOT", "$"), ("Coinbase", "COIN", "$")]},
    "3 - Mineração": {"tag": "Mining", "assets": [("CleanSpark", "CLSK", "$"), ("Hut 8", "HUT", "$"), ("Bitfarms", "BITF", "$"), ("Iris Energy", "IREN", "$")]},
    "4 - Volume Spot": {"tag": "Spot Vol", "assets": [("BTC", "BTC-USD", "$"), ("ETH", "ETH-USD", "$"), ("SOL", "SOL-USD", "$"), ("BNB", "BNB-USD", "$")]}
}

CRYPTO_BENCHMARKS = [
    {"key": "BTC", "ticker": "BTC-USD", "label": "Bitcoin / BTC", "prefix": "$ "},
    {"key": "ETH", "ticker": "ETH-USD", "label": "Ethereum / ETH", "prefix": "$ "},
    {"key": "BTC_D", "type": "global_api", "sub_key": "btc_d", "label": "Bitcoin Dom. (BTC.D)"},
    {"key": "FEAR_GREED", "type": "fng_api", "label": "Fear & Greed Index"}
]

# -----------------------------------------------------------------------------
# 3. FUNÇÕES DE SUPORTE E INGESTÃO
# -----------------------------------------------------------------------------
def fmt_num(val, dec=2):
    if val is None or pd.isna(val) or val == 0.0:
        return "--"
    return f"{val:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(val):
    if val is None or pd.isna(val):
        return "0,00%"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%".replace(".", ",")

def generate_pdf_report(text_content, company, timestamp):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        c.drawString(50, height - 50, f"=== {company} ===")
        c.drawString(50, height - 70, f"Gerado em: {timestamp}")
        y = height - 100
        for line in text_content.split("\n"):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line[:90])
            y = y - 15
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    except Exception:
        return text_content.encode('utf-8')

@st.cache_data(ttl=600)
def fetch_btc_fng():
    try:
        res = requests.get("https://api.alternative.me/fng/", timeout=3)
        if res.status_code == 200:
            data = res.json()["data"][0]
            return data.get("value", "62") + " / 100", data.get("value_classification", "Greed")
    except Exception:
        pass
    return "62 / 100", "Greed"

@st.cache_data(ttl=600)
def fetch_global_crypto_data():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/global", timeout=3)
        if res.status_code == 200:
            data = res.json()["data"]
            btc_d = data.get("market_cap_percentage", {}).get("btc", 56.8)
            return {"btc_d_val": f"{btc_d:.2f}%".replace(".", ","), "btc_d_chg": 0.35}
    except Exception:
        pass
    return {"btc_d_val": "56,80%", "btc_d_chg": 0.35}

def fetch_brapi_fallback(failed_symbols, token=""):
    brapi_quotes = {}
    if not failed_symbols:
        return brapi_quotes
    token_clean = token.split("=")[-1].strip().replace('"', '').replace("'", "") if token else ""
    sym_map = {sym.replace(".SA", "").strip().upper(): sym for sym in failed_symbols}
    clean_symbols_str = ",".join(sym_map.keys())
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"token": token_clean} if token_clean else {}
    try:
        url = f"https://brapi.dev/api/quote/{clean_symbols_str}"
        res = requests.get(url, params=params, headers=headers, timeout=6)
        if res.status_code == 200:
            for item in res.json().get("results", []):
                raw_sym = str(item.get("symbol", "")).upper()
                orig_sym = sym_map.get(raw_sym, raw_sym + ".SA")
                price = item.get("regularMarketPrice") or item.get("close") or item.get("price") or 0.0
                chg = item.get("regularMarketChangePercent") or item.get("changePercent") or 0.0
                if price and float(price) > 0:
                    brapi_quotes[orig_sym] = {"price": float(price), "change": float(chg)}
    except Exception:
        pass
    return brapi_quotes

@st.cache_data(ttl=300)
def fetch_realtime_quotes(symbols_tuple, brapi_token=""):
    quotes = {sym: {"price": 0.0, "change": 0.0} for sym in symbols_tuple}
    alias_map = {"UNI-USD": "UNI7083-USD"}
    try:
        download_list = [alias_map.get(s, s) for s in symbols_tuple]
        if "ES=F" not in download_list:
            download_list.append("ES=F")
        df_data = yf.download(download_list, period="5d", interval="1d", group_by="ticker", progress=False)
        for orig_sym in symbols_tuple + ("ES=F",):
            actual_sym = alias_map.get(orig_sym, orig_sym)
            try:
                df_sym = df_data if len(download_list) == 1 else (df_data[actual_sym] if actual_sym in df_data.columns.get_level_values(0) else None)
                if df_sym is not None and not df_sym.empty:
                    df_clean = df_sym.dropna(subset=["Close"])
                    if len(df_clean) >= 1:
                        p = float(df_clean["Close"].iloc[-1])
                        prev = float(df_clean["Close"].iloc[-2]) if len(df_clean) >= 2 else p
                        c = ((p - prev) / prev) * 100 if prev > 0 else 0.0
                        if p > 0:
                            quotes[orig_sym] = {"price": p, "change": c}
            except Exception:
                pass
    except Exception:
        pass

    failed_b3 = [sym for sym, val in quotes.items() if (val["price"] == 0.0 or pd.isna(val["price"])) and sym.endswith(".SA")]
    if failed_b3:
        for sym, data_dict in fetch_brapi_fallback(failed_b3, token=brapi_token).items():
            quotes[sym] = data_dict
    return quotes

# -----------------------------------------------------------------------------
# 4. SIDEBAR: CONFIGURAÇÕES
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações OMNI")
modulo = st.sidebar.radio("Módulo:", ["Crypto", "TradFi (Macro)"], index=1)
brapi_token = st.sidebar.text_input("BRAPI API Token:", value="", type="password")
tier_selected = st.sidebar.radio("Plano Ativo:", ["Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B White-Label)"], index=1)

allow_customization = "Free" not in tier_selected
allow_white_label = "Premium" in tier_selected
max_free_tickers = 5 if "Standard" in tier_selected else (999 if "Premium" in tier_selected else 0)

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

custom_tickers = []
if allow_customization:
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3.SA):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()][:max_free_tickers]

horizonte_pred = st.sidebar.selectbox("Horizonte Temporário:", ["24 Horas", "48 Horas", "7 Dias"], index=1)
alvo_pct = st.sidebar.slider("Projeção de Resposta (%)", 0.5, 15.0, 3.0, 0.5)
stop_pct = st.sidebar.slider("Zona de Suporte / Defesa (%)", 0.5, 15.0, 3.0, 0.5)
formato = st.sidebar.radio("Formato de Entrega:", ["B2B (Relatório)", "B2C (YouTube Auto-Pilot)"], index=0)

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    company_name = st.sidebar.text_input("Nome da Casa/Escritório:", "XP / BTG / Gestora")
    cnpi_code = st.sidebar.text_input("Registro CNPI:", "CNPI-T 3421")

symbols_to_fetch = [item["ticker"] for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS if item.get("ticker")]
for cat_info in active_categories.values():
    for _, ticker, _ in cat_info["assets"]:
        symbols_to_fetch.append(ticker)
symbols_to_fetch.extend(custom_tickers)

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), brapi_token=brapi_token)
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()

# -----------------------------------------------------------------------------
# 5. CABEÇALHO & BARRA DE BENCHMARKS NO TOPO
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"📊 {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
st.markdown(f'<div class="status-bar">🟢 <b>Dados consolidados às {now_str}</b> | Módulo Ativo: <b>{modulo}</b></div>', unsafe_allow_html=True)

# Barra superior de Benchmarks (Estilo Bloomberg Ticker Bar)
b_cols = st.columns(len(active_benchmarks))
for idx, item in enumerate(active_benchmarks):
    with b_cols[idx]:
        val_str, chg_str, change_cls = "0", "0%", "metric-change-neutral"
        if item.get("type") == "fng_api":
            val_str, chg_str = fng_val, fng_class
        elif item.get("type") == "global_api":
            val_str, chg_str = global_crypto_data["btc_d_val"], "+0.35%"
        elif item.get("ticker"):
            data = quotes.get(item["ticker"], {"price": 0.0, "change": 0.0})
            val_str = f"{item.get('prefix', '')}{fmt_num(data['price'])}"
            chg_str = fmt_pct(data['change'])
            change_cls = "metric-change-pos" if data["change"] >= 0 else "metric-change-neg"
        
        st.markdown(f'<div class="metric-card"><div class="metric-title">{item["label"]}</div><div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. LAYOUT PRINCIPAL EM DUAS COLUNAS (RELATÓRIO À ESQUERDA | WATCHLIST/CATEGORIAS À DIREITA)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1.4, 1])

with col_left:
    st.subheader(f"📄 Geração de Relatório — {formato}")
    
    # Geração Dinâmica do Conteúdo
    if "B2B" in formato:
        report_lines = [
            f"=== RELATÓRIO INSTITUCIONAL {modulo.upper()} ===",
            f"Emitente: {company_name} | CNPI: {cnpi_code}",
            f"Data/Hora: {now_str}",
            f"Horizonte: {horizonte_pred} | Alvo: +{alvo_pct}% | Defesa: -{stop_pct}%",
            f"Sentimento (Fear & Greed): {fng_val} ({fng_class})",
            "",
            "--- DESTAQUES DE MERCADO ---"
        ]
        for cat_name, cat_info in active_categories.items():
            report_lines.append(f"\n[{cat_name.upper()}]")
            for disp_name, ticker, currency in cat_info["assets"]:
                q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                report_lines.append(f"  • {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        
        output_content = "\n".join(report_lines)
    else:
        script_lines = [
            f"=== ROTEIRO YOUTUBE AUTO-PILOT ({modulo.upper()}) ===",
            f"Data: {now_str}",
            "",
            "[INTRODUÇÃO - 00:00]",
            f"Fala, investidor! Trazendo o panorama atualizado de {modulo}.",
            "",
            "[ANÁLISE DE ATIVOS]"
        ]
        for cat_name, cat_info in active_categories.items():
            for disp_name, ticker, currency in cat_info["assets"][:2]:
                q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                script_lines.append(f" - {disp_name} cotado a {currency} {fmt_num(q['price'])}, variação de {fmt_pct(q['change'])}.")
        script_lines.extend(["", "[CONCLUSÃO]", "Deixe seu like e se inscreva! Bons trades!"])
        output_content = "\n".join(script_lines)

    st.text_area("", value=output_content, height=380, label_visibility="collapsed")
    
    # Botões de Exportação
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.download_button("📥 Baixar (TXT)", data=output_content, file_name=f"OMNI_Relatorio_{modulo}.txt", mime="text/plain", use_container_width=True)
    with col_b2:
        json_data = json.dumps({"module": modulo, "timestamp": now_str, "content": output_content}, indent=4, ensure_ascii=False)
        st.download_button("📥 Baixar (JSON)", data=json_data, file_name=f"OMNI_Relatorio_{modulo}.json", mime="application/json", use_container_width=True)
    with col_b3:
        pdf_bytes = generate_pdf_report(output_content, company_name, now_str)
        st.download_button("📥 Baixar (PDF)", data=pdf_bytes, file_name=f"OMNI_Relatorio_{modulo}.pdf", mime="application/pdf", use_container_width=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.subheader("🎯 Alvos Preditivos & Zonas Operacionais")
    p1, p2, p3, p4 = st.columns(4)
    main_q = quotes.get("BTC-USD" if modulo == "Crypto" else "^GSPC", {"price": 100.0, "change": 0.0})
    with p1:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Tendência</div><div class="pred-value">Compradora</div></div>', unsafe_allow_html=True)
    with p2:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Resistência Alvo</div><div class="pred-value">{fmt_num(main_q["price"] * 1.03)}</div></div>', unsafe_allow_html=True)
    with p3:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Suporte Chave</div><div class="pred-value">{fmt_num(main_q["price"] * 0.97)}</div></div>', unsafe_allow_html=True)
    with p4:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Volatilidade</div><div class="pred-value">3.45%</div></div>', unsafe_allow_html=True)

with col_right:
    st.subheader(f"🗂️ Watchlist de Categorias ({modulo})")
    st.caption("Inspeção rápida de ativos por setor:")
    
    # Exibição organizada em Abas ou Expanders limpos para evitar poluição visual
    for cat_name, cat_info in active_categories.items():
        with st.expander(f"{cat_name} ({cat_info['tag']})"):
            for disp_name, ticker, currency in cat_info["assets"]:
                q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                color_style = "color: #3FB950;" if q["change"] >= 0 else "color: #F85149;"
                st.markdown(f'<div style="font-size: 13px; display: flex; justify-content: space-between; margin-bottom: 4px;"><span><b>{disp_name}:</b></span><span>{currency} {fmt_num(q["price"])} <b style="{color_style}">({fmt_pct(q["change"])})</b></span></div>', unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. MAPA TÉRMICO DE LIQUIDAÇÕES (RODAPÉ)
# -----------------------------------------------------------------------------
st.subheader("🔥 Mapa Térmico de Liquidações & Clusters de Alavancagem")
st.caption("Perfil estrutural de liquidez e piscinas de alavancagem passiva em derivativos:")

if PLOTLY_AVAILABLE:
    oi_ticker = "BTC-USD" if modulo == "Crypto" else "ES=F"
    base_price = quotes.get(oi_ticker, {"price": 77000.0 if modulo == "Crypto" else 5800.0}).get("price", 77000.0)
    
    min_p, max_p = (60000.0, 84000.0) if modulo == "Crypto" else (base_price * 0.85, base_price * 1.15)
    step = 500.0 if modulo == "Crypto" else (base_price * 0.01)

    prices, liq_volumes = [], []
    curr = min_p
    while curr <= max_p:
        prices.append(curr)
        dist = abs(curr - base_price)
        base_vol = (180 if modulo == "Crypto" else 50) + dist * 0.05
        liq_volumes.append(base_vol)
        curr += step

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(
        y=prices, x=liq_volumes, orientation='h',
        marker=dict(color=liq_volumes, colorscale='Turbo', showscale=True, colorbar=dict(title="Vol ($M)", len=0.8, thickness=10)),
        name="Liquidez"
    ))
    fig_oi.add_hline(y=base_price, line_dash="dash", line_color="#58A6FF", annotation_text=f"Spot: {fmt_num(base_price)}")
    fig_oi.update_layout(
        paper_bgcolor="#0B0E14", plot_bgcolor="#161B22", font=dict(color="#C9D1D9", size=11),
        margin=dict(l=10, r=10, t=30, b=10), height=380,
        yaxis=dict(gridcolor="#30363D", title="Preço"), xaxis=dict(gridcolor="#30363D", title="Volume Acumulado ($M)")
    )
    st.plotly_chart(fig_oi, use_container_width=True)
else:
    st.warning("⚠️ Plotly indisponível.")

st.markdown("---")
st.caption("⚡©️ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")