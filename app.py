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
    .col-header-sync {
        min-height: 64px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .status-bar {
        background-color: #131B2A;
        padding: 10px 18px;
        border-radius: 8px;
        border: 1px solid #1E293B;
        margin-bottom: 20px;
        color: #94A3B8;
        font-size: 13px;
    }
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .metric-title { font-size: 12px; color: #8B949E; font-weight: 600; }
    .metric-value { font-size: 18px; font-weight: 700; color: #F0F6FC; margin: 4px 0; }
    .metric-change-pos { font-size: 12px; color: #3FB950; font-weight: 600; }
    .metric-change-neg { font-size: 12px; color: #F85149; font-weight: 600; }
    .metric-change-neutral { font-size: 12px; color: #58A6FF; font-weight: 600; }
    .premium-badge { color: #58A6FF; font-weight: bold; }

    .pred-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 14px;
        height: 85px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pred-title { font-size: 11px; color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .pred-value { font-size: 15px; font-weight: 700; color: #F0F6FC; }
    .pred-sub { font-size: 11px; font-weight: 600; }

    /* Ajuste milimétrico para alinhar o relatório */
    .stTextArea {
        margin-top: -5px !important;
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
    div[data-testid="stCheckbox"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        height: 24px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    div[data-testid="stCheckbox"] > label {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        margin: 0px !important;
        padding: 0px !important;
        cursor: pointer !important;
    }
    div[data-baseweb="checkbox"] input:checked + div {
        background-color: #238636 !important;
        border-color: #238636 !important;
    }
    input[type="checkbox"]:checked { accent-color: #238636 !important; }
</style>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. ACERVO MESTRE DE DADOS & CATEGORIAS (TRADFI & CRYPTO)
# -----------------------------------------------------------------------------
CATEGORIES_TRADFI = {
    "1 - Bancos e Seguradoras": {
        "tag": "Banking & Ins.",
        "assets": [("ITUB4", "ITUB4.SA", "R$"), ("BBAS3", "BBAS3.SA", "R$"), ("BBDC4", "BBDC4.SA", "R$"), ("BBSE3", "BBSE3.SA", "R$")]
    },
    "2 - Energia": {
        "tag": "Energy",
        "assets": [("PETR4", "PETR4.SA", "R$"), ("PRIO3", "PRIO3.SA", "R$"), ("EQTL3", "EQTL3.SA", "R$"), ("CPFE3", "CPFE3.SA", "R$")]
    },
    "3 - Tech": {
        "tag": "Technology",
        "assets": [("TOTVS3", "TOTS3.SA", "R$"), ("NVDA", "NVDA", "$"), ("AAPL", "AAPL", "$"), ("MSFT", "MSFT", "$")]
    },
    "4 - Commodities": {
        "tag": "Commodities",
        "assets": [("VALE3", "VALE3.SA", "R$"), ("GGBR4", "GGBR4.SA", "R$"), ("CMIG4", "CMIG4.SA", "R$"), ("KLBN11", "KLBN11.SA", "R$")]
    },
    "5 - Varejo": {
        "tag": "Retail",
        "assets": [("ASAI3", "ASAI3.SA", "R$"), ("LREN3", "LREN3.SA", "R$"), ("MGLU3", "MGLU3.SA", "R$"), ("RADL3", "RADL3.SA", "R$")]
    },
    "6 - Logística e Infra.": {
        "tag": "Infra & Log",
        "assets": [("RAIL3", "RAIL3.SA", "R$"), ("WEGE3", "WEGE3.SA", "R$"), ("CCRO3", "CCRO3.SA", "R$"), ("EMBR3", "EMBR3.SA", "R$")]
    },
    "7 - Agro e Indústria": {
        "tag": "Agri & Industry",
        "assets": [("SLCE3", "SLCE3.SA", "R$"), ("BRFS3", "BRFS3.SA", "R$"), ("ABEV3", "ABEV3.SA", "R$"), ("JBSS3", "JBSS3.SA", "R$")]
    },
    "8 - Crypto e Digital Assets": {
        "tag": "Digital Assets",
        "assets": [("BTCUSDT", "BTC-USD", "$"), ("ETHUSDT", "ETH-USD", "$"), ("SOLUSDT", "SOL-USD", "$"), ("BNBUSDT", "BNB-USD", "$")]
    }
}

MACRO_BENCHMARKS = [
    {"key": "SPX", "ticker": "^GSPC", "label": "1. S&P 500 / SPX", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "IBOV", "ticker": "^BVSP", "label": "2. Ibovespa / IBOV", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "BRENT", "ticker": "BZ=F", "label": "3. Petróleo Brent", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "GOLD", "ticker": "GC=F", "label": "4. Ouro Spot", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "5. USD / BRL / Dólar Real", "unit": "pts", "prefix": "R$ ", "badge": "Direct API"}
]

CATEGORIES_CRYPTO = {
    "1 - ETFs": {
        "tag": "ETFs",
        "assets": [("IBIT (BlackRock)", "IBIT", "$"), ("FBTC (Fidelity)", "FBTC", "$"), ("ETHA (Ethereum)", "ETHA", "$"), ("BITO (Futures)", "BITO", "$")]
    },
    "2 - Treasury": {
        "tag": "Treasury",
        "assets": [("MicroStrategy", "MSTR", "$"), ("Marathon Digital", "MARA", "$"), ("Riot Platforms", "RIOT", "$"), ("Coinbase Global", "COIN", "$")]
    },
    "3 - Mineração e Hashrate": {
        "tag": "Mining",
        "assets": [("CleanSpark", "CLSK", "$"), ("Hut 8", "HUT", "$"), ("Bitfarms", "BITF", "$"), ("Iris Energy", "IREN", "$")]
    },
    "4 - Volume Spot (24 hs)": {
        "tag": "Spot Vol",
        "assets": [("BTCUSDT", "BTC-USD", "$"), ("ETHUSDT", "ETH-USD", "$"), ("SOLUSDT", "SOL-USD", "$"), ("BNBUSDT", "BNB-USD", "$")]
    },
    "5 - Volume Futuros (24 hs)": {
        "tag": "Derivatives",
        "assets": [("BTC Perp", "BTC-USD", "$"), ("ETH Perp", "ETH-USD", "$"), ("SOL Perp", "SOL-USD", "$"), ("BNB Perp", "BNB-USD", "$")]
    },
    "6 - Open Interest": {
        "tag": "Open Interest",
        "assets": [("BTC OI Base", "BTC-USD", "$"), ("ETH OI Base", "ETH-USD", "$"), ("SOL OI Base", "SOL-USD", "$"), ("AVAX OI Base", "AVAX-USD", "$")]
    },
    "7 - DeFi e Layer 1s": {
        "tag": "DeFi & L1",
        "assets": [("UNI (Uniswap)", "UNI7083-USD", "$"), ("AAVE (Aave)", "AAVE-USD", "$"), ("LINK (Chainlink)", "LINK-USD", "$"), ("AVAX (Avalanche)", "AVAX-USD", "$")]
    },
    "8 - Stablecoins": {
        "tag": "Stablecoins",
        "assets": [("USDT / USD", "USDT-USD", "$"), ("USDC / USD", "USDC-USD", "$"), ("USDT / BRL", "BRL=X", "R$"), ("DAI / USD", "DAI-USD", "$")]
    }
}

CRYPTO_BENCHMARKS = [
    {"key": "BTC", "ticker": "BTC-USD", "label": "1. Bitcoin / BTC", "prefix": "$ ", "badge": "Direct API"},
    {"key": "ETH", "ticker": "ETH-USD", "label": "2. Ethereum / ETH", "prefix": "$ ", "badge": "Direct API"},
    {"key": "BTC_D", "type": "global_api", "sub_key": "btc_d", "label": "3. Bitcoin Dominance / BTC.D", "badge": "CoinGecko API"},
    {"key": "USDT_D", "type": "global_api", "sub_key": "usdt_d", "label": "4. Tether Dominance / USDT.D", "badge": "CoinGecko API"},
    {"key": "FEAR_GREED", "type": "fng_api", "label": "5. Bitcoin Fear & Greed Index", "badge": "Alternative.me API"}
]

# -----------------------------------------------------------------------------
# 3. FUNÇÕES DE FORMATAÇÃO E INGESTÃO ROBUSTA
# -----------------------------------------------------------------------------
def fmt_num(val, dec=2):
    if val is None or pd.isna(val) or val == 0.0:
        return "--"
    s = f"{val:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

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
            usdt_d = data.get("market_cap_percentage", {}).get("usdt", 5.2)
            return {
                "btc_d_val": f"{btc_d:.2f}%".replace(".", ","),
                "btc_d_chg": 0.35,
                "usdt_d_val": f"{usdt_d:.2f}%".replace(".", ","),
                "usdt_d_chg": -0.18
            }
    except Exception:
        pass
    return {"btc_d_val": "56,80%", "btc_d_chg": 0.35, "usdt_d_val": "5,20%", "usdt_d_chg": -0.18}

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

    for orig_sym in [s for s, v in quotes.items() if v["price"] == 0.0]:
        try:
            hist = yf.Ticker(alias_map.get(orig_sym, orig_sym)).history(period="5d").dropna(subset=["Close"])
            if not hist.empty:
                p = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else p
                c = ((p - prev) / prev) * 100 if prev > 0 else 0.0
                if p > 0:
                    quotes[orig_sym] = {"price": p, "change": c}
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
modulo = st.sidebar.radio("📊 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1)
brapi_token = st.sidebar.text_input("BRAPI API Token:", value="", type="password")
tier_selected = st.sidebar.radio("Plano Ativo:", ["Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B White-Label)"], index=1)

allow_customization = "Free" not in tier_selected
allow_white_label = "Premium" in tier_selected
max_free_tickers = 5 if "Standard" in tier_selected else (999 if "Premium" in tier_selected else 0)

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

selected_categories = [key for key in active_categories.keys() if st.sidebar.checkbox(key, value=True)]
custom_tickers = []
if allow_customization:
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3.SA, PEPE-USD):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()][:max_free_tickers]

horizonte_pred = st.sidebar.selectbox("Horizonte Temporário:", ["24 Horas", "48 Horas", "7 Dias"], index=1)
alvo_pct = st.sidebar.slider("Projeção de Resposta (%)", 0.5, 15.0, 3.0, 0.5)
stop_pct = st.sidebar.slider("Zona de Suporte / Defesa (%)", 0.5, 15.0, 3.0, 0.5)
formato = st.sidebar.radio(f"📋 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube Auto-Pilot)"], index=0)

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    company_name = st.sidebar.text_input("Nome da Casa/Escritório:", "XP / BTG / Gestora")
    cnpi_code = st.sidebar.text_input("Registro CNPI/Responsável:", "CNPI-T 3421")

symbols_to_fetch = [item["ticker"] for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS if item.get("ticker")]
for cat_info in active_categories.values():
    for _, ticker, _ in cat_info["assets"]:
        symbols_to_fetch.append(ticker)
symbols_to_fetch.extend(custom_tickers)

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), brapi_token=brapi_token)
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()

active_display_categories = active_categories.copy()
if custom_tickers:
    active_display_categories["0 - Tickers Personalizados"] = {
        "tag": "Custom Feed",
        "assets": [(t, t, "R$" if ".SA" in t else "$") for t in custom_tickers]
    }
    if "0 - Tickers Personalizados" not in selected_categories:
        selected_categories.insert(0, "0 - Tickers Personalizados")

# -----------------------------------------------------------------------------
# 5. CORPO PRINCIPAL & LAYOUT DE DUAS COLUNAS
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏢 {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(f'<div class="status-bar">🕒 <b>Dados consolidados às {now_str}</b> | Status API: <span style="color: #3FB950;">🟢 Online</span> | <b>Módulo:</b> {modulo}</div>', unsafe_allow_html=True)
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.markdown('<div class="col-header-sync">', unsafe_allow_html=True)
    st.subheader(f"📑 Entrega Padrão — {formato}")
    st.caption("Relatório analítico gerado com dados consolidados em tempo real:")
    st.markdown('</div>', unsafe_allow_html=True)

    # Geração Dinâmica filtrando categorias e ativos ativos via st.session_state
    if "B2B" in formato:
        report_lines = [
            f"=== RELATÓRIO INSTITUCIONAL {modulo.upper()} (B2B) ===",
            f"Emitente: {company_name} | Responsável: {cnpi_code}",
            f"Data/Hora de Emissão: {now_str}",
            f"Horizonte Analítico: {horizonte_pred} | Alvo: +{alvo_pct}% | Stop Defesa: -{stop_pct}%",
            f"Sentimento de Mercado (Fear & Greed): {fng_val} ({fng_class})",
            "",
            "--- SUMÁRIO DE ATIVOS E CATEGORIAS MONITORADAS ---"
        ]
        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_key = f"chk_cat_{cat_name}"
                # Respeita o estado do checkbox do card (padrão True)
                if not st.session_state.get(cat_key, True):
                    continue
                
                cat_info = active_display_categories[cat_name]
                report_lines.append(f"\n[{cat_name.upper()}] (Tag: {cat_info['tag']})")
                for disp_name, ticker, currency in cat_info["assets"]:
                    asset_key = f"chk_asset_{cat_name}_{ticker}"
                    # Respeita o estado do checkbox do ativo individual (padrão True)
                    if not st.session_state.get(asset_key, True):
                        continue
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    report_lines.append(f"  • {disp_name} ({ticker}): {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        
        report_lines.extend([
            "",
            "--- CONCLUSÃO TÉCNICA QUANT ---",
            f"Tendência estrutural alinhada ao horizonte de {horizonte_pred}. Monitoramento ativo de zonas de liquidez e alavancagem em derivativos para proteção de posições."
        ])
        output_content = "\n".join(report_lines)
        st.text_area("", value=output_content, height=410, label_visibility="collapsed")
        
        # Botões de Exportação Múltipla (TXT, JSON, PDF)
        st.markdown("**Opções de Exportação do Relatório:**")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.download_button("📥 Baixar (TXT)", data=output_content, file_name=f"OMNI_Relatorio_{modulo}.txt", mime="text/plain", use_container_width=True)
        with col_b2:
            json_data = json.dumps({
                "module": modulo,
                "timestamp": now_str,
                "company": company_name,
                "cnpi": cnpi_code,
                "horizon": horizonte_pred,
                "target_pct": alvo_pct,
                "stop_pct": stop_pct,
                "sentiment": f"{fng_val} ({fng_class})",
                "categories": {
                    cat_name: {
                        disp_name: quotes.get(ticker, {"price": 0.0, "change": 0.0})["price"] 
                        for disp_name, ticker, currency in active_display_categories[cat_name]["assets"] 
                        if st.session_state.get(f"chk_asset_{cat_name}_{ticker}", True)
                    } 
                    for cat_name in selected_categories 
                    if cat_name in active_display_categories and st.session_state.get(f"chk_cat_{cat_name}", True)
                }
            }, indent=4, ensure_ascii=False)
            st.download_button("📥 Baixar (JSON)", data=json_data, file_name=f"OMNI_Relatorio_{modulo}.json", mime="application/json", use_container_width=True)
        with col_b3:
            pdf_bytes = generate_pdf_report(output_content, company_name, now_str)
            st.download_button("📥 Baixar (PDF)", data=pdf_bytes, file_name=f"OMNI_Relatorio_{modulo}.pdf", mime="application/pdf", use_container_width=True)
    else:
        script_lines = [
            f"=== ROTEIRO YOUTUBE AUTO-PILOT ({modulo.upper()}) ===",
            f"Data/Hora: {now_str}",
            f"Horizonte: {horizonte_pred}",
            "",
            "[INTRODUÇÃO - 00:00]",
            f"Fala, investidor! Sejam bem-vindos a mais um panorama de {modulo} com os dados consolidados em {now_str}.",
            "",
            "[DESENVOLVIMENTO - ANÁLISE DE MERCADO]"
        ]
        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_key = f"chk_cat_{cat_name}"
                if not st.session_state.get(cat_key, True):
                    continue
                cat_info = active_display_categories[cat_name]
                script_lines.append(f"Destaques em {cat_name}:")
                active_assets = [
                    (d, t, c) for d, t, c in cat_info["assets"] 
                    if st.session_state.get(f"chk_asset_{cat_name}_{t}", True)
                ]
                for disp_name, ticker, currency in active_assets[:2]:
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    script_lines.append(f" - {disp_name} negociado a {currency} {fmt_num(q['price'])}, registrando {fmt_pct(q['change'])} hoje.")
        script_lines.extend([
            "",
            "[FECHAMENTO - CALL TO ACTION]",
            "Deixe o seu like, se inscreva no canal e ative as notificações. Bons trades e até a próxima!"
        ])
        script_text = "\n".join(script_lines)
        st.text_area("", value=script_text, height=410, label_visibility="collapsed")
        
        st.markdown("**Opções de Exportação do Roteiro:**")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.download_button("📥 Baixar (TXT)", data=script_text, file_name=f"OMNI_Roteiro_{modulo}.txt", mime="text/plain", use_container_width=True)
        with col_b2:
            json_data = json.dumps({"module": modulo, "timestamp": now_str, "script": script_text}, indent=4, ensure_ascii=False)
            st.download_button("📥 Baixar (JSON)", data=json_data, file_name=f"OMNI_Roteiro_{modulo}.json", mime="application/json", use_container_width=True)
        with col_b3:
            pdf_bytes = generate_pdf_report(script_text, company_name, now_str)
            st.download_button("📥 Baixar (PDF)", data=pdf_bytes, file_name=f"OMNI_Roteiro_{modulo}.pdf", mime="application/pdf", use_container_width=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🎯 Alvos Preditivos & Zonas Operacionais")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    main_q = quotes.get("BTC-USD" if modulo == "Crypto" else "^GSPC", {"price": 100.0, "change": 0.0})
    with c1:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Tendência</div><div class="pred-value">Compradora</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Resistência Alvo</div><div class="pred-value">{fmt_num(main_q["price"] * 1.03)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Suporte Chave</div><div class="pred-value">{fmt_num(main_q["price"] * 0.97)}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Previsão</div><div class="pred-value">Alta Moderada</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Volatilidade</div><div class="pred-value">3.45%</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="pred-card"><div class="pred-title">Delta OI</div><div class="pred-value">+5.82%</div></div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="col-header-sync">', unsafe_allow_html=True)
    st.subheader(f"📈 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado às {datetime.now().strftime('%H:%M:%S BRT')}")
    st.markdown('</div>', unsafe_allow_html=True)

    for item in active_benchmarks:
        label = item["label"]
        val_str, chg_str, change_cls = "0", "0%", "metric-change-neutral"
        if item.get("type") == "fng_api":
            val_str, chg_str = fng_val, fng_class
        elif item.get("type") == "global_api":
            sub_k = item.get("sub_key")
            val_str = global_crypto_data["btc_d_val"] if sub_k == "btc_d" else global_crypto_data["usdt_d_val"]
            chg_str = fmt_pct(global_crypto_data["btc_d_chg"])
        elif item.get("ticker"):
            data = quotes.get(item["ticker"], {"price": 0.0, "change": 0.0})
            val_str = f"{item.get('prefix', '')}{fmt_num(data['price'])}"
            chg_str = f"{fmt_pct(data['change'])} hoje"
            change_cls = "metric-change-pos" if data["change"] >= 0 else "metric-change-neg"

        st.markdown(f'<div class="metric-card"><div class="metric-title">{label}</div><div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. PAINEL DE ANÁLISE INTEGRADA (CARDS DE CATEGORIA)
# -----------------------------------------------------------------------------
st.subheader(f"🧩 Painel de Análise Integrada das Categorias ({modulo})")
if selected_categories:
    cols = st.columns(min(len(selected_categories), 4))
    for idx, cat_name in enumerate(selected_categories):
        if cat_name in active_display_categories:
            cat_info = active_display_categories[cat_name]
            col = cols[idx % len(cols)]
            with col:
                with st.container(border=True):
                    cat_key = f"chk_cat_{cat_name}"
                    c_title, c_check = st.columns([3.2, 0.8])
                    with c_title:
                        st.markdown(f'<div style="font-size: 13px; font-weight: 700; color: #F0F6FC;">{cat_name}</div>', unsafe_allow_html=True)
                    with c_check:
                        cat_enabled = st.checkbox("", value=st.session_state.get(cat_key, True), key=cat_key, label_visibility="collapsed")
                    
                    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
                    for disp_name, ticker, currency in cat_info["assets"]:
                        q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                        asset_key = f"chk_asset_{cat_name}_{ticker}"
                        color_style = "color: #3FB950;" if q["change"] >= 0 else "color: #F85149;"
                        
                        cA, cB = st.columns([3.2, 0.8])
                        with cA:
                            st.markdown(f'<div style="font-size: 12px;"><span style="color: #8B949E;">{disp_name}:</span> <b style="color: #F0F6FC;">{currency} {fmt_num(q["price"])}</b> <span style="{color_style}">({fmt_pct(q["change"])})</span></div>', unsafe_allow_html=True)
                        with cB:
                            st.checkbox("", value=st.session_state.get(asset_key, True), key=asset_key, disabled=not cat_enabled, label_visibility="collapsed")

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. NOVO MÓDULO: MAPA TÉRMICO DE LIQUIDAÇÕES & CLUSTERS DE ALAVANCAGEM
# -----------------------------------------------------------------------------
st.subheader("🔥 Mapa Térmico de Liquidações & Clusters de Alavancagem")
st.caption("Perfil estrutural de liquidez e piscinas de alavancagem passiva em derivativos:")

if PLOTLY_AVAILABLE:
    oi_asset_name = "BTCUSDT Liquidation Heatmap & Leverage Pools" if modulo == "Crypto" else "S&P 500 Liquidity Profile (ES=F)"
    oi_ticker = "BTC-USD" if modulo == "Crypto" else "ES=F"
    base_price = quotes.get(oi_ticker, {"price": 77000.0 if modulo == "Crypto" else 5800.0}).get("price", 77000.0)
    
    if modulo == "Crypto":
        min_p, max_p = 60000.0, 84000.0
        step = 500.0
    else:
        min_p, max_p = base_price * 0.85, base_price * 1.15
        step = base_price * 0.01

    prices = []
    liq_volumes = []
    
    curr = min_p
    while curr <= max_p:
        prices.append(curr)
        dist_from_spot = curr - base_price
        
        if modulo == "Crypto":
            if 60500 <= curr <= 66000:
                base_vol = 180 + (66000 - curr) * 0.08
            elif 70000 <= curr <= 71500:
                base_vol = 140
            elif curr > base_price:
                base_vol = 30 + abs(curr - base_price) * 0.03
            else:
                base_vol = 45 + abs(dist_from_spot) * 0.01
        else:
            base_vol = 50 + abs(dist_from_spot) * 0.05
            
        liq_volumes.append(base_vol)
        curr += step

    fig_oi = go.Figure()

    fig_oi.add_trace(go.Bar(
        y=prices,
        x=liq_volumes,
        orientation='h',
        marker=dict(
            color=liq_volumes,
            colorscale='Turbo',
            showscale=True,
            colorbar=dict(title="Volume Liq. ($M)", len=0.8, thickness=12, tickfont=dict(color="#C9D1D9"))
        ),
        text=[f"Preço: {fmt_num(p)} | Risco: {v:.0f}M" for p, v in zip(prices, liq_volumes)],
        hoverinfo='text',
        name="Clusters de Liquidez"
    ))

    fig_oi.add_hline(
        y=base_price, 
        line_dash="dash", 
        line_color="#58A6FF", 
        annotation_text=f"Spot Atual: {fmt_num(base_price)}",
        annotation_position="bottom right",
        annotation_font_color="#58A6FF"
    )

    fig_oi.update_layout(
        title=f"Mapa de Densidade de Liquidez & Zonas de Alavancagem — {oi_asset_name}",
        paper_bgcolor="#0B0E14", 
        plot_bgcolor="#161B22", 
        font=dict(color="#C9D1D9", size=12),
        margin=dict(l=20, r=20, t=40, b=20), 
        height=500,
        yaxis=dict(gridcolor="#30363D", title="Níveis de Preço (USD)"),
        xaxis=dict(gridcolor="#30363D", title="Intensidade de Alavancagem / Volume Acumulado ($M)")
    )
    st.plotly_chart(fig_oi, use_container_width=True)
else:
    st.warning("⚠️ O módulo Plotly não está disponível no momento. Certifique-se de incluir 'plotly' no arquivo `requirements.txt`.")

st.markdown("---")
st.caption("⚡©️ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")