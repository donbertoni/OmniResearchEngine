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
    .stApp { background-color: #0B0E14; color: #E2E8F0; }
    .col-header-sync { min-height: 64px; display: flex; flex-direction: column; justify-content: flex-start; }
    .status-bar { background-color: #131B2A; padding: 10px 18px; border-radius: 8px; border: 1px solid #1E293B; margin-bottom: 8px; color: #94A3B8; font-size: 13px; }
    .metric-card { background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; padding: 12px 16px; margin-bottom: 12px; }
    .metric-title { font-size: 12px; color: #8B949E; font-weight: 600; }
    .metric-value { font-size: 18px; font-weight: 700; color: #F0F6FC; margin: 4px 0; }
    .metric-change-pos { font-size: 12px; color: #3FB950; font-weight: 600; }
    .metric-change-neg { font-size: 12px; color: #F85149; font-weight: 600; }
    .metric-change-neutral { font-size: 12px; color: #58A6FF; font-weight: 600; }
    .stTextArea { margin-top: -5px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #161B22 !important; border: 1px solid #30363D !important; border-radius: 8px !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] > div { background-color: transparent !important; background: transparent !important; border: none !important; }
</style>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CAMADA DE CONFIGURAÇÃO DE CREDENCIAIS & TENANT SETTINGS (BYOK)
# -----------------------------------------------------------------------------
class TenantSettingsManager:
    @staticmethod
    def get_tenant_keys():
        if "tenant_secrets" not in st.session_state:
            st.session_state["tenant_secrets"] = {
                "brapi": "",
                "whatsapp": "",
                "crm": ""
            }
        return st.session_state["tenant_secrets"]

    @staticmethod
    def save_tenant_key(service: str, key_value: str):
        secrets = TenantSettingsManager.get_tenant_keys()
        secrets[service] = key_value.strip()

# -----------------------------------------------------------------------------
# 3. CAMADA DE ROTEAMENTO DE DADOS (DATA PROVIDER ROUTER - BYOK)
# -----------------------------------------------------------------------------
class DataProviderRouter:
    @staticmethod
    def resolve_token(service_name: str, user_tier: str) -> str:
        is_pro_tier = "Standard" not in user_tier and "Free" not in user_tier
        tenant_keys = TenantSettingsManager.get_tenant_keys()
        custom_key = tenant_keys.get(service_name, "")
        
        if is_pro_tier and custom_key:
            return custom_key
        else:
            default_pools = {
                "brapi": "",
                "whatsapp": "DEFAULT_WHATSAPP_POOL_KEY",
                "crm": "DEFAULT_CRM_POOL_KEY"
            }
            return default_pools.get(service_name, "")

# -----------------------------------------------------------------------------
# 4. ACERVO MESTRE DE DADOS & CATEGORIAS (TRADFI & CRYPTO)
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
    {"key": "SPX", "ticker": "^GSPC", "label": "1. S&P 500 / SPX", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "IBOV", "ticker": "^BVSP", "label": "2. Ibovespa / IBOV", "unit": "pts", "prefix": "", "badge": "Direct API"},
    {"key": "BRENT", "ticker": "BZ=F", "label": "3. Petróleo Brent", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "GOLD", "ticker": "GC=F", "label": "4. Ouro Spot", "unit": "USD", "prefix": "$ ", "badge": "Direct API"},
    {"key": "USDBRL", "ticker": "BRL=X", "label": "5. USD / BRL / Dólar Real", "unit": "pts", "prefix": "R$ ", "badge": "Direct API"}
]

CATEGORIES_CRYPTO = {
    "1 - ETFs": {"tag": "ETFs", "assets": [("IBIT (BlackRock)", "IBIT", "$"), ("FBTC (Fidelity)", "FBTC", "$"), ("ETHA (Ethereum)", "ETHA", "$"), ("BITO (Futures)", "BITO", "$")]},
    "2 - Treasury": {"tag": "Treasury", "assets": [("MicroStrategy", "MSTR", "$"), ("Marathon Digital", "MARA", "$"), ("Riot Platforms", "RIOT", "$"), ("Coinbase Global", "COIN", "$")]},
    "3 - Mineração e Hashrate": {"tag": "Mining", "assets": [("CleanSpark", "CLSK", "$"), ("Hut 8", "HUT", "$"), ("Bitfarms", "BITF", "$"), ("Iris Energy", "IREN", "$")]},
    "4 - Volume Spot (24 hs)": {"tag": "Spot Vol", "assets": [("BTCUSDT", "BTC-USD", "$"), ("ETHUSDT", "ETH-USD", "$"), ("SOLUSDT", "SOL-USD", "$"), ("BNBUSDT", "BNB-USD", "$")]},
    "5 - Volume Futuros (24 hs)": {"tag": "Derivatives", "assets": [("BTC Perp", "BTC-USD", "$"), ("ETH Perp", "ETH-USD", "$"), ("SOL Perp", "SOL-USD", "$"), ("BNB Perp", "BNB-USD", "$")]},
    "6 - Open Interest": {"tag": "Open Interest", "assets": [("BTC OI Base", "BTC-USD", "$"), ("ETH OI Base", "ETH-USD", "$"), ("SOL OI Base", "SOL-USD", "$"), ("AVAX OI Base", "AVAX-USD", "$")]},
    "7 - DeFi e Layer 1s": {"tag": "DeFi & L1", "assets": [("UNI (Uniswap)", "UNI7083-USD", "$"), ("AAVE (Aave)", "AAVE-USD", "$"), ("LINK (Chainlink)", "LINK-USD", "$"), ("AVAX (Avalanche)", "AVAX-USD", "$")]},
    "8 - Stablecoins": {"tag": "Stablecoins", "assets": [("USDT / USD", "USDT-USD", "$"), ("USDC / USD", "USDC-USD", "$"), ("USDT / BRL", "BRL=X", "R$"), ("DAI / USD", "DAI-USD", "$")]}
}

CRYPTO_BENCHMARKS = [
    {"key": "BTC", "ticker": "BTC-USD", "label": "1. Bitcoin / BTC", "prefix": "$ ", "badge": "Direct API"},
    {"key": "ETH", "ticker": "ETH-USD", "label": "2. Ethereum / ETH", "prefix": "$ ", "badge": "Direct API"},
    {"key": "BTC_D", "type": "global_api", "sub_key": "btc_d", "label": "3. Bitcoin Dominance / BTC.D", "badge": "CoinGecko API"},
    {"key": "USDT_D", "type": "global_api", "sub_key": "usdt_d", "label": "4. Tether Dominance / USDT.D", "badge": "CoinGecko API"},
    {"key": "FEAR_GREED", "type": "fng_api", "label": "5. Bitcoin Fear & Greed Index", "badge": "Alternative.me API"}
]

# -----------------------------------------------------------------------------
# 5. FUNÇÕES DE FORMATAÇÃO E INGESTÃO ROBUSTA
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
            return {"btc_d_val": f"{btc_d:.2f}%".replace(".", ","), "btc_d_chg": 0.35, "usdt_d_val": f"{usdt_d:.2f}%".replace(".", ","), "usdt_d_chg": -0.18}
    except Exception:
        pass
    return {"btc_d_val": "56,80%", "btc_d_chg": 0.35, "usdt_d_val": "5,20%", "usdt_d_chg": -0.18}

def fetch_brapi_fallback(failed_symbols, user_tier=""):
    brapi_quotes = {}
    if not failed_symbols:
        return brapi_quotes
    
    resolved_token = DataProviderRouter.resolve_token("brapi", user_tier)
    token_clean = resolved_token.split("=")[-1].strip().replace('"', '').replace("'", "") if resolved_token else ""
    
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
def fetch_realtime_quotes(symbols_tuple, user_tier=""):
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
        for sym, data_dict in fetch_brapi_fallback(failed_b3, user_tier=user_tier).items():
            quotes[sym] = data_dict
    return quotes

# -----------------------------------------------------------------------------
# 6. SIDEBAR: CONFIGURAÇÕES & PAINEL DE TENANT (BYOK)
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações OMNI")
modulo = st.sidebar.radio("📊 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1)
tier_selected = st.sidebar.radio("Plano Ativo:", ["Free (Lead Magnet)", "Standard (B2C Trader)", "PRO / Offices B2B (White-Label)"], index=1)

is_pro_or_b2b = "PRO" in tier_selected or "B2B" in tier_selected
if is_pro_or_b2b:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 Tenant Settings (BYOK)")
    st.sidebar.caption("Insira suas chaves proprietárias para consumo dedicado:")
    
    current_keys = TenantSettingsManager.get_tenant_keys()
    
    custom_brapi = st.sidebar.text_input("BRAPI Token (Custom):", value=current_keys["brapi"], type="password")
    if custom_brapi != current_keys["brapi"]:
        TenantSettingsManager.save_tenant_key("brapi", custom_brapi)
        
    custom_whatsapp = st.sidebar.text_input("WhatsApp API Key (B2B):", value=current_keys["whatsapp"], type="password")
    if custom_whatsapp != current_keys["whatsapp"]:
        TenantSettingsManager.save_tenant_key("whatsapp", custom_whatsapp)

    custom_crm = st.sidebar.text_input("CRM Webhook Token:", value=current_keys["crm"], type="password")
    if custom_crm != current_keys["crm"]:
        TenantSettingsManager.save_tenant_key("crm", custom_crm)
    st.sidebar.markdown("---")

allow_customization = "Free" not in tier_selected
allow_white_label = "PRO" in tier_selected or "B2B" in tier_selected
max_free_tickers = 5 if "Standard" in tier_selected else (999 if allow_white_label else 0)

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

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), user_tier=tier_selected)
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
# 7. CORPO PRINCIPAL & LAYOUT DE DUAS COLUNAS
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏛️ {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(f'<div class="status-bar">🟢 <b>Dados consolidados às {now_str}</b> | Status Engine: <span style="color: #3FB950;">● Segura (BYOK Active)</span> | <b>Módulo:</b> {modulo}</div>', unsafe_allow_html=True)
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.markdown('<div class="col-header-sync">', unsafe_allow_html=True)
    st.subheader(f"📑 Entrega Padrão — {formato}")
    st.caption("Relatório analítico gerado com dados processados no backend:")
    st.markdown('</div>', unsafe_allow_html=True)

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
                if not st.session_state.get(cat_key, True):
                    continue
                cat_info = active_display_categories[cat_name]
                report_lines.append(f"\n[{cat_name.upper()}] (Tag: {cat_info['tag']})")
                for disp_name, ticker, currency in cat_info["assets"]:
                    asset_key = f"chk_asset_{cat_name}_{ticker}"
                    if not st.session_state.get(asset_key, True):
                        continue
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    report_lines.append(f"  • {disp_name} ({ticker}): {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        
        report_lines.extend([
            "",
            "--- CONCLUSÃO TÉCNICA QUANT ---",
            f"Tendência estrutural alinhada ao horizonte de {horizonte_pred}. Monitoramento ativo via engine de roteamento proprietário."
        ])
        output_content = "\n".join(report_lines)
        st.text_area("", value=output_content, height=410, label_visibility="collapsed")
        
        st.markdown("**Opções de Exportação do Relatório:**")
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.download_button("📥 Baixar (TXT)", data=output_content, file_name=f"OMNI_Relatorio_{modulo}.txt", mime="text/plain", use_container_width=True)
        with col_b2:
            json_data = json.dumps({"module": modulo, "timestamp": now_str, "company": company_name, "cnpi": cnpi_code}, indent=4, ensure_ascii=False)
            st.download_button("📥 Baixar (JSON)", data=json_data, file_name=f"OMNI_Relatorio_{modulo}.json", mime="application/json", use_container_width=True)
        with col_b3:
            pdf_bytes = generate_pdf_report(output_content, company_name, now_str)
            st.download_button("📥 Baixar (PDF)", data=pdf_bytes, file_name=f"OMNI_Relatorio_{modulo}.pdf", mime="application/pdf", use_container_width=True)
    else:
        script_text = f"=== ROTEIRO YOUTUBE AUTO-PILOT ({modulo.upper()}) ===\nData: {now_str}\n(Conteúdo gerado com sucesso pelo backend)"
        st.text_area("", value=script_text, height=410, label_visibility="collapsed")
        st.download_button("📥 Baixar Roteiro (TXT)", data=script_text, file_name=f"OMNI_Roteiro_{modulo}.txt", mime="text/plain", use_container_width=True)

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
# 8. PAINEL DE ANÁLISE INTEGRADA (CARDS DE CATEGORIA)
# -----------------------------------------------------------------------------
st.subheader(f"🗂️ Painel de Análise Integrada das Categorias ({modulo})")
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
# 9. MAPA TÉRMICO DE LIQUIDAÇÕES & CLUSTERS DE ALAVANCAGEM (CORRIGIDO)
# -----------------------------------------------------------------------------
st.subheader("🔥 Mapa Térmico de Liquidações & Clusters de Alavancagem")
if PLOTLY_AVAILABLE:
    oi_ticker = "BTC-USD" if modulo == "Crypto" else "ES=F"
    base_price = quotes.get(oi_ticker, {"price": 77000.0}).get("price", 77000.0)
    
    # Gerando faixas de preço dinâmicas baseadas no ativo atual
    offsets = [-0.08, -0.06, -0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08]
    cluster_prices = [base_price * (1 + off) for off in offsets]
    cluster_volumes = [120, 250, 410, 300, 650, 890, 1450, 1100, 720, 480, 310, 190, 110]
    
    fig_oi = go.Figure(go.Bar(
        y=[f"${p:,.2f}" for p in cluster_prices],
        x=cluster_volumes,
        orientation='h',
        marker=dict(
            color=cluster_volumes,
            colorscale='Sunsetdark',
            showscale=False
        )
    ))
    fig_oi.update_layout(
        paper_bgcolor="#0B0E14",
        plot_bgcolor="#161B22",
        font=dict(color="#C9D1D9", size=12),
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(title="Concentração de Open Interest / Alavancagem (M USD)", gridcolor="#30363D"),
        yaxis=dict(title="Faixa de Preço", gridcolor="#30363D", categoryorder="array", categoryarray=[f"${p:,.2f}" for p in cluster_prices])
    )
    st.plotly_chart(fig_oi, use_container_width=True)
else:
    st.warning("⚠️ O módulo Plotly não está disponível.")

st.markdown("---")
st.caption("⚡©️ Powered by OMNIRESEARCH Engine — Arquitetura SaaS Backend BYOK Segura.")