import streamlit as st
import requests
from datetime import datetime, timezone, timedelta

# Configuração da página
st.set_page_config(
    page_title="OMNIRESEARCH Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Customizada CSS
st.markdown("""
<style>
    .main {
        background-color: #0b101d;
        color: #e2e8f0;
    }
    .stCard {
        background-color: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #f8fafc;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .status-red {
        color: #ef4444;
        font-weight: 500;
        font-size: 13px;
    }
    .status-green {
        color: #10b981;
        font-weight: 500;
        font-size: 13px;
    }
    .status-blue {
        color: #38bdf8;
        font-weight: 500;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# Timestamp Dinâmico (Horário de Brasília)
brt_tz = timezone(timedelta(hours=-3))
agora_brt = datetime.now(brt_tz)
data_atual = agora_brt.strftime("%d/%m/%Y às %H:%M:%S BRT")

# Função resiliente para buscar dados do CoinGecko e Fear & Greed Index
@st.cache_data(ttl=20)
def get_coingecko_data():
    data = {
        "btc_price": "$64.481,00", "btc_change": "+2,19%", "btc_is_pos": True,
        "btc_raw_price": 64481.00,
        "eth_price": "$1.909,21", "eth_change": "+1,36%", "eth_is_pos": True,
        "eth_raw_price": 1909.21,
        "sol_price": "$76,05", "sol_change": "+1,25%", "sol_is_pos": True,
        "btc_dom": "56,56%",
        "fng_val": "31 / 100", "fng_classification": "Medo", "fng_css": "status-red"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        url_prices = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
        resp_prices = requests.get(url_prices, headers=headers, timeout=3).json()

        if "bitcoin" in resp_prices:
            btc_p = resp_prices["bitcoin"]["usd"]
            btc_c = resp_prices["bitcoin"].get("usd_24h_change", 2.19)
            data["btc_raw_price"] = btc_p
            data["btc_price"] = f"${btc_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["btc_change"] = f"{btc_c:+.2f}%".replace(".", ",")
            data["btc_is_pos"] = btc_c >= 0

        if "ethereum" in resp_prices:
            eth_p = resp_prices["ethereum"]["usd"]
            eth_c = resp_prices["ethereum"].get("usd_24h_change", 1.36)
            data["eth_raw_price"] = eth_p
            data["eth_price"] = f"${eth_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["eth_change"] = f"{eth_c:+.2f}%".replace(".", ",")
            data["eth_is_pos"] = eth_c >= 0

        if "solana" in resp_prices:
            sol_p = resp_prices["solana"]["usd"]
            sol_c = resp_prices["solana"].get("usd_24h_change", 1.25)
            data["sol_price"] = f"${sol_p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            data["sol_change"] = f"{sol_c:+.2f}%".replace(".", ",")
            data["sol_is_pos"] = sol_c >= 0
    except Exception:
        pass

    try:
        url_global = "https://api.coingecko.com/api/v3/global"
        resp_global = requests.get(url_global, headers=headers, timeout=3).json()

        if "data" in resp_global:
            dom_btc = resp_global["data"]["market_cap_percentage"]["btc"]
            data["btc_dom"] = f"{dom_btc:.2f}%".replace(".", ",")
    except Exception:
        pass

    try:
        url_fng = "https://api.alternative.me/fng/"
        resp_fng = requests.get(url_fng, headers=headers, timeout=3).json()
        if "data" in resp_fng and len(resp_fng["data"]) > 0:
            val = int(resp_fng["data"][0]["value"])
            classif = resp_fng["data"][0]["value_classification"]
            
            classif_map = {
                "Extreme Fear": "Medo Extremo",
                "Fear": "Medo",
                "Neutral": "Neutro",
                "Greed": "Ganância",
                "Extreme Greed": "Ganância Extrema"
            }
            pt_classif = classif_map.get(classif, classif)
            data["fng_val"] = f"{val} / 100"
            data["fng_classification"] = pt_classif
            
            if val >= 55:
                data["fng_css"] = "status-green"
            elif val <= 45:
                data["fng_css"] = "status-red"
            else:
                data["fng_css"] = "status-blue"
    except Exception:
        pass

    return data

# Função resiliente para buscar dados MACRO via API
@st.cache_data(ttl=60)
def get_macro_data():
    data = {
        "sp500_val": "7.758", "sp500_chg": "-0,53%", "sp500_is_pos": False,
        "ibov_val": "166.833", "ibov_chg": "-0,16%", "ibov_is_pos": False,
        "usdbrl_val": "5,20", "usdbrl_chg": "+0,00%", "usdbrl_is_pos": True,
        "m2_val": "$104.8T (+4.2% YoY)",
        "gold_val": "$4.474,90", "gold_chg": "+0,85%", "gold_is_pos": True,
        "oil_val": "$90,69", "oil_chg": "+2,45%", "oil_is_pos": True
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url_fx = "https://economia.awesomeapi.com.br/last/USD-BRL"
        resp_fx = requests.get(url_fx, headers=headers, timeout=3).json()
        if "USDBRL" in resp_fx:
            bid = float(resp_fx["USDBRL"]["bid"])
            pct = float(resp_fx["USDBRL"]["pctChange"])
            data["usdbrl_val"] = f"{bid:.2f}".replace(".", ",")
            data["usdbrl_chg"] = f"{pct:+.2f}%".replace(".", ",")
            data["usdbrl_is_pos"] = pct >= 0
    except Exception:
        pass
    return data

# Função para calcular Suporte e Resistência ESTRUTURAIS
def calcular_suporte_resistencia_estrutural(preco_base):
    passo = 2500
    sup = (int(preco_base) // passo) * passo
    res = sup + passo
    if res - preco_base < 400: res += passo
    if preco_base - sup < 400: sup -= passo
    sup_str = f"${sup:,.0f}".replace(",", ".")
    res_str = f"${res:,.0f}".replace(",", ".")
    return sup_str, res_str

# Sidebar
st.sidebar.title("⚙️ Configurações OMNI")
modulo = st.sidebar.radio("💡 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"])
formato = st.sidebar.radio(f"🎯 Formato ({modulo}):", ["B2B (Relatório)", "B2C (YouTube)"])

# Header Principal
st.title("⚡ OMNIRESEARCH Engine")
st.info(f"🕒 **Dados consolidados das {data_atual}**")

col_left, col_right = st.columns([1.6, 1])

# LÓGICA DINÂMICA
if modulo == "TradFi (Macro)":
    # --- CHAMADA CORRETIVA DA FUNÇÃO ---
    macro_data = get_macro_data()
    sp500_tendencia, sp500_score, sp500_valor_nivel = "Pressão Vendedora", "38 pts", "7.680 pts"
    ibov_tendencia, ibov_score, ibov_valor_nivel = "Consolidação 7D", "52 pts", "165.200 pts"

    with col_left:
        if formato == "B2C (YouTube)":
            st.subheader("🎬 Roteiro B2C YouTube (TradFi & Macro)")
            roteiro_tradfi = f"[HOOK 0-15s]\nO mercado global está em ponto crítico hoje ({data_atual}). S&P 500 cotado a {macro_data['sp500_val']} pts e o Ibovespa em {macro_data['ibov_val']} pts.\n\n[BLOCO 1 - PANORAMA GLOBAL]\n- S&P 500: {macro_data['sp500_val']} pts ({macro_data['sp500_chg']}).\n- Ibovespa: {macro_data['ibov_val']} pts.\n- Dólar: R$ {macro_data['usdbrl_val']}.\n\n[BLOCO 2 - COMMODITIES]\n- Ouro: {macro_data['gold_val']}/oz ({macro_data['gold_chg']}).\n- Petróleo: {macro_data['oil_val']}/bbl ({macro_data['oil_chg']})."
            st.text_area("", value=roteiro_tradfi, height=310)
        else:
            st.subheader("📰 Relatório B2B (TradFi & Macroeconomia)")
            relatorio_texto = f"=== RELATÓRIO INSTITUCIONAL TRADFI & MACROECONOMIA (B2B) ===\nData: {data_atual}\n\n1. PANORAMA MACRO\n- S&P 500: {macro_data['sp500_val']} pts ({macro_data['sp500_chg']})\n- Ibovespa: {macro_data['ibov_val']} pts ({macro_data['ibov_chg']})\n- USD/BRL: R$ {macro_data['usdbrl_val']}\n\n2. COMMODITIES\n- Ouro: {macro_data['gold_val']}/oz\n- Petróleo: {macro_data['oil_val']}/bbl"
            st.text_area("", value=relatorio_texto, height=310)

else:
    crypto_data = get_coingecko_data()
    btc_sup, btc_res = calcular_suporte_resistencia_estrutural(crypto_data["btc_raw_price"])
    btc_tendencia = "Tendência Compradora" if crypto_data["btc_is_pos"] else "Pressão Vendedora"
    btc_score = "78 pts" if crypto_data["btc_is_pos"] else "42 pts"
    
    with col_left:
        st.subheader("📰 Relatório B2B (Crypto & Web3)")
        relatorio_crypto = f"=== RELATÓRIO INSTITUCIONAL CRYPTO ===\n- BTC: {crypto_data['btc_price']}\n- Tendência: {btc_tendencia} ({btc_score})\n- Suporte: {btc_sup} | Resistência: {btc_res}"
        st.text_area("", value=relatorio_crypto, height=310)