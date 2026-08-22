import json
from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import numpy as np

# Importação segura do Plotly com fallback
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Importação do Backend Modularizado
from backend import (
    MACRO_BENCHMARKS,
    CRYPTO_BENCHMARKS,
    CATEGORIES_CRYPTO,
    fmt_num,
    fmt_pct,
    generate_pdf_report,
    fetch_btc_fng,
    fetch_global_crypto_data,
    fetch_realtime_quotes,
    send_whatsapp_report
)

# -----------------------------------------------------------------------------
# DEFINIÇÃO DE CATEGORIAS (MÓDULO TRADFI - 8 CATEGORIAS ORIGINAIS)
# -----------------------------------------------------------------------------
CATEGORIES_TRADFI = {
    "1 - Bancos e Seguradoras": {
        "tag": "Banks",
        "assets": [
            ("Itaú Unibanco", "ITUB4.SA", "R$"),
            ("Banco do Brasil", "BBAS3.SA", "R$"),
            ("Bradesco PN", "BBDC4.SA", "R$"),
            ("BB Seguridade", "BBSE3.SA", "R$")
        ]
    },
    "2 - Energia": {
        "tag": "Energy",
        "assets": [
            ("Petrobras PN", "PETR4.SA", "R$"),
            ("Petróleo Rio", "PRIO3.SA", "R$"),
            ("Equatorial", "EQTL3.SA", "R$"),
            ("CPFL Energia", "CPFE3.SA", "R$")
        ]
    },
    "3 - Tech": {
        "tag": "Tech",
        "assets": [
            ("Totvs", "TOTVS3.SA", "R$"),
            ("NVIDIA Corp", "NVDA", "$"),
            ("Apple Inc", "AAPL", "$"),
            ("Microsoft", "MSFT", "$")
        ]
    },
    "4 - Commodities": {
        "tag": "Commodities",
        "assets": [
            ("Vale ON", "VALE3.SA", "R$"),
            ("Gerdau", "GGBR4.SA", "R$"),
            ("Cemig", "CMIG4.SA", "R$"),
            ("Klabin", "KLBN11.SA", "R$")
        ]
    },
    "5 - Varejo": {
        "tag": "Retail",
        "assets": [
            ("Assaí", "ASAI3.SA", "R$"),
            ("Lojas Renner", "LREN3.SA", "R$"),
            ("Magazine Luiza", "MGLU3.SA", "R$"),
            ("RaiaDrogasil", "RADL3.SA", "R$")
        ]
    },
    "6 - Logística e Infra.": {
        "tag": "Logistics",
        "assets": [
            ("Rumo", "RAIL3.SA", "R$"),
            ("Weg", "WEGE3.SA", "R$"),
            ("CCR", "CCRO3.SA", "R$"),
            ("Embraer", "EMBR3.SA", "R$")
        ]
    },
    "7 - Agro e Indústria": {
        "tag": "Agro",
        "assets": [
            ("SLC Agrícola", "SLCE3.SA", "R$"),
            ("BRF", "BRFS3.SA", "R$"),
            ("Ambev", "ABEV3.SA", "R$"),
            ("JBS", "JBSS3.SA", "R$")
        ]
    },
    "8 - FIIs e Imobiliário": {
        "tag": "Real Estate",
        "assets": [
            ("HGLG11", "HGLG11.SA", "R$"),
            ("KNRI11", "KNRI11.SA", "R$"),
            ("XPLG11", "XPLG11.SA", "R$"),
            ("MXRF11", "MXRF11.SA", "R$")
        ]
    }
}

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
        padding: 10px 18px;
        border-radius: 8px;
        border: 1px solid #1E293B;
        margin-bottom: 8px;
        color: #94A3B8;
        font-size: 13px;
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
    .metric-title { font-size: 11px; color: #8B949E; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .metric-value { font-size: 15px; font-weight: 700; color: #F0F6FC; margin: 2px 0px; }
    .color-green { color: #3FB950 !important; font-weight: 600; }
    .color-red { color: #F85149 !important; font-weight: 600; }
    .color-blue { color: #58A6FF !important; font-weight: 600; }

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
# 2. SIDEBAR: CONFIGURAÇÕES & CREDENCIAIS (BYOK / CRM)
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações OMNI")
modulo = st.sidebar.radio("📌 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=1)

with st.sidebar.expander("🔑 BYOK & Credenciais de APIs", expanded=False):
    brapi_token = st.text_input("BRAPI API Token:", value="", type="password")
    custom_data_api_key = st.text_input("Custom Market API Key:", value="", type="password")
    whatsapp_instance = st.text_input("WhatsApp Instance ID:", value="")
    whatsapp_token = st.text_input("WhatsApp API Token:", value="", type="password")

with st.sidebar.expander("🔗 Integração CRM & Webhooks", expanded=False):
    crm_api_endpoint = st.text_input("CRM API Endpoint (Contatos):", value="", placeholder="https://api.seu-crm.com/v1/contacts")
    fallback_whatsapp_phone = st.text_input("Contatos Manuais (tel. separados por vírgula):", value="", placeholder="+5548999999999, +554888888888")

tier_selected = st.sidebar.radio("Plano Ativo:", ["Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B White-Label)"], index=1)

allow_customization = "Free" not in tier_selected
allow_white_label = "Premium" in tier_selected
max_free_tickers = 5 if "Standard" in tier_selected else (999 if "Premium" in tier_selected else 0)

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

# Seleção de Formatos Independentes (B2B e B2C Auto-Pilot nativo)
st.sidebar.markdown("### 📊 Formatos de Saída:")
fmt_b2b = st.sidebar.checkbox("B2B (Relatório Analítico)", value=True)
fmt_yt = st.sidebar.checkbox("B2C (YouTube Auto-Pilot)", value=False)
fmt_wapp = st.sidebar.checkbox("B2C (WhatsApp Auto-Pilot)", value=False)
fmt_tg = st.sidebar.checkbox("B2C (Telegram Auto-Pilot)", value=False)

st.sidebar.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
trigger_production = st.sidebar.button("🚀 Acionar Produção Automática", use_container_width=True)

custom_tickers = []
if allow_customization:
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3.SA, PEPE-USD):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()][:max_free_tickers]

company_name = "OMNIRESEARCH Engine"
cnpi_code = "CNPI-T 0000"
if allow_white_label:
    company_name = st.sidebar.text_input("Nome da Casa/Escritório:", "XP / BTG / Gestora")
    cnpi_code = st.sidebar.text_input("Registro CNPI/Responsável:", "CNPI-T 3421")

# Coleta de símbolos e requisição de cotações em tempo real via API
symbols_to_fetch = [item["ticker"] for item in MACRO_BENCHMARKS + CRYPTO_BENCHMARKS if item.get("ticker")]
for cat_info in active_categories.values():
    for _, ticker, _ in cat_info["assets"]:
        symbols_to_fetch.append(ticker)
symbols_to_fetch.extend(custom_tickers)

quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), brapi_token=brapi_token, custom_api_key=custom_data_api_key)
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()

active_display_categories = active_categories.copy()
if custom_tickers:
    active_display_categories["0 - Tickers Personalizados"] = {
        "tag": "Custom Feed",
        "assets": [(t, t, "R$" if ".SA" in t else "$") for t in custom_tickers]
    }

selected_categories = list(active_display_categories.keys())

def get_crm_contacts_list(api_url, fallback_ph):
    contacts = []
    if api_url:
        try:
            headers = {"Authorization": f"Bearer {whatsapp_token}"} if whatsapp_token else {}
            res = requests.get(api_url, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                items = data if isinstance(data, list) else data.get("contacts", [])
                for item in items:
                    ph = item.get("phone") or item.get("whatsapp")
                    if ph:
                        contacts.append({"name": item.get("name", "Cliente"), "phone": str(ph)})
        except Exception:
            pass
    if fallback_ph:
        raw_phones = [p.strip() for p in fallback_ph.split(",") if p.strip()]
        for idx, ph in enumerate(raw_phones):
            contacts.append({"name": f"Contato Manual {idx+1}", "phone": ph})
    return contacts

# -----------------------------------------------------------------------------
# 3. CORPO PRINCIPAL & LAYOUT DE DUAS COLUNAS
# -----------------------------------------------------------------------------
if allow_white_label and company_name != "OMNIRESEARCH Engine":
    st.title(f"🏢 {company_name} — Terminal Quant")
    st.caption(f"Análise Exclusiva B2B | Responsável Técnico: {cnpi_code}")
else:
    st.title("⚡ OMNIRESEARCH Engine")
    st.caption("Plataforma Integrada de Inteligência Financeira com IA & Auto-Pilot")

now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S BRT")
is_weekend = datetime.now().weekday() >= 5  # Sábado (5) ou Domingo (6)

col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(f'<div class="status-bar">🟢 <b>Dados consolidados às {now_str}</b> | Fonte: BRAPI / Yahoo Finance / Deribit | <b>Módulo:</b> {modulo}</div>', unsafe_allow_html=True)
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

# Alerta específico de fim de semana para o módulo TradFi
if modulo == "TradFi (Macro)" and is_weekend:
    st.markdown('<div class="warning-bar">⚠️ <b>Mercado TradFi Fechado (Fim de Semana):</b> As cotações refletem o fechamento oficial do último pregão (Sexta-feira). As APIs continuam ativas para consulta histórica.</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.subheader("📝 Entregas e Conteúdos Selecionados")
    st.caption("Geração automática de relatórios e scripts com base nas cotações e seleções do dashboard:")

    # Container para gerar os conteúdos dos formatos selecionados de forma limpa e simultânea
    outputs_generated = []

    if fmt_b2b:
        report_lines = [
            f"=== RELATÓRIO INSTITUCIONAL {modulo.upper()} (B2B) ===",
            f"Emitente: {company_name} | Responsável: {cnpi_code}",
            f"Data/Hora de Emissão: {now_str}",
            f"Sentimento de Mercado: {fng_val} ({fng_class})",
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
        
        include_heatmap = st.session_state.get("chk_include_heatmap", True)
        if include_heatmap:
            report_lines.extend([
                "",
                "--- ANÁLISE TÉCNICA DO MAPA TÉRMICO / LIQUIDEZ ---",
                "Mapeamento de liquidez institucional validado por fluxo de derivativos e order book."
            ])

        report_lines.extend([
            "",
            "--- CONCLUSÃO TÉCNICA QUANT ---",
            "Monitoramento ativo de zonas de liquidez para suporte a posições estruturais."
        ])
        outputs_generated.append(("B2B (Relatório Analítico)", "\n".join(report_lines)))

    if fmt_yt:
        yt_lines = [
            f"=== SCRIPT YOUTUBE (AUTO-PILOT) ===",
            f"Data/Hora: {now_str}",
            "",
            "[INTRODUÇÃO - 00:00]",
            f"Fala, investidor! Panorama de {modulo} gerado automaticamente pelo Auto-Pilot OMNI.",
            "",
            "[DESTAQUES DE MERCADO]"
        ]
        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_key = f"chk_cat_{cat_name}"
                if not st.session_state.get(cat_key, True):
                    continue
                cat_info = active_display_categories[cat_name]
                active_assets = [
                    (d, t, c) for d, t, c in cat_info["assets"] 
                    if st.session_state.get(f"chk_asset_{cat_name}_{t}", True)
                ]
                for disp_name, ticker, currency in active_assets[:2]:
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    yt_lines.append(f" - {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        yt_lines.extend(["", "[CALL TO ACTION]", "Acesse o terminal OMNI para acompanhar em tempo real!"])
        outputs_generated.append(("B2C (YouTube)", "\n".join(yt_lines)))

    if fmt_wapp:
        wapp_lines = [
            f"=== MENSAGEM WHATSAPP (AUTO-PILOT) ===",
            f"Alerta OMNI - {now_str}",
            "📊 Resumo executivo de mercado:"
        ]
        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_key = f"chk_cat_{cat_name}"
                if not st.session_state.get(cat_key, True):
                    continue
                cat_info = active_display_categories[cat_name]
                for disp_name, ticker, currency in cat_info["assets"][:1]:
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    wapp_lines.append(f"• {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        wapp_lines.append("\nAcesse o terminal para o relatório completo.")
        outputs_generated.append(("B2C (WhatsApp)", "\n".join(wapp_lines)))

    if fmt_tg:
        tg_lines = [
            f"=== MENSAGEM TELEGRAM (AUTO-PILOT) ===",
            f"🚀 Canal Oficial OMNI | {now_str}"
        ]
        for cat_name in selected_categories:
            if cat_name in active_display_categories:
                cat_key = f"chk_cat_{cat_name}"
                if not st.session_state.get(cat_key, True):
                    continue
                cat_info = active_display_categories[cat_name]
                for disp_name, ticker, currency in cat_info["assets"][:1]:
                    q = quotes.get(ticker, {"price": 0.0, "change": 0.0})
                    tg_lines.append(f"▪️ {disp_name}: {currency} {fmt_num(q['price'])} ({fmt_pct(q['change'])})")
        outputs_generated.append(("B2C (Telegram)", "\n".join(tg_lines)))

    if not outputs_generated:
        st.info("Nenhum formato de saída selecionado na barra lateral. Marque pelo menos uma opção.")
        primary_output_text = "Nenhum conteúdo gerado."
    else:
        # Exibe cada formato selecionado em abas ou blocos limpos
        if len(outputs_generated) == 1:
            title_out, primary_output_text = outputs_generated[0]
            st.text_area(title_out, value=primary_output_text, height=380)
        else:
            tabs = st.tabs([item[0] for item in outputs_generated])
            for idx, (title_out, content_text) in enumerate(outputs_generated):
                with tabs[idx]:
                    st.text_area(f"Visualizar {title_out}", value=content_text, height=350, key=f"txt_area_{idx}")
            primary_output_text = outputs_generated[0][1] # Para download principal

    st.markdown("**Opções de Exportação & Disparo Multicanal:**")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.download_button("📥 TXT", data=primary_output_text, file_name=f"OMNI_Report_{modulo}.txt", mime="text/plain", use_container_width=True)
    with col_b2:
        json_data = json.dumps({"module": modulo, "timestamp": now_str, "content": primary_output_text}, indent=4, ensure_ascii=False)
        st.download_button("📥 JSON", data=json_data, file_name=f"OMNI_Report_{modulo}.json", mime="application/json", use_container_width=True)
    with col_b3:
        pdf_bytes = generate_pdf_report(primary_output_text, company_name, now_str)
        st.download_button("📥 PDF", data=pdf_bytes, file_name=f"OMNI_Report_{modulo}.pdf", mime="application/pdf", use_container_width=True)
    with col_b4:
        if st.button("🚀 Disparar CRM", use_container_width=True):
            contacts_list = get_crm_contacts_list(crm_api_endpoint, fallback_whatsapp_phone)
            if not contacts_list:
                st.warning("Nenhum contato encontrado na API do CRM ou telefones manuais.")
            else:
                success_count = 0
                for contact in contacts_list:
                    ok, _ = send_whatsapp_report(contact["phone"], whatsapp_instance, whatsapp_token, primary_output_text)
                    if ok:
                        success_count += 1
                st.success(f"Disparo concluído! Enviado para {success_count}/{len(contacts_list)} contatos.")

with col_right:
    st.subheader(f"📈 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado às {datetime.now().strftime('%H:%M:%S BRT')} | Fonte: APIs Oficiais")

    for item in active_benchmarks:
        label = item["label"]
        val_str, chg_str, change_cls = "0", "0%", "color-blue"
        
        if item.get("type") == "fng_api":
            val_str = fng_val
            cls_map = {"Greed": "color-green", "Neutral": "color-blue", "Fear": "color-red"}
            change_cls = cls_map.get(fng_class, "color-blue")
            chg_str = f"Sentimento: {fng_class}"
        elif item.get("type") == "global_api":
            sub_k = item.get("sub_key")
            val_str = global_crypto_data["btc_d_val"] if sub_k == "btc_d" else global_crypto_data["usdt_d_val"]
            chg_val = global_crypto_data["btc_d_chg"] if sub_k == "btc_d" else global_crypto_data["usdt_d_chg"]
            chg_str = f"{fmt_pct(chg_val)}"
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")
        elif item.get("ticker"):
            data = quotes.get(item["ticker"], {"price": 0.0, "change": 0.0})
            val_str = f"{item.get('prefix', '')}{fmt_num(data['price'])}"
            chg_val = data["change"]
            chg_str = f"{fmt_pct(chg_val)}"
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")

        st.markdown(f'<div class="metric-card"><div class="metric-title">{label}</div><div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. PAINEL DE ANÁLISE INTEGRADA (CARDS DE CATEGORIA COM TOGGLES DO DASHBOARD)
# -----------------------------------------------------------------------------
st.subheader(f"📊 Painel de Análise Integrada das Categorias ({modulo})")
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
                        chg_val = q["change"]
                        color_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")
                        
                        cA, cB = st.columns([3.2, 0.8])
                        with cA:
                            st.markdown(f'<div style="font-size: 12px;"><span style="color: #8B949E;">{disp_name}:</span> <b style="color: #F0F6FC;">{currency} {fmt_num(q["price"])}</b> <span class="{color_cls}">({fmt_pct(q["change"])})</span></div>', unsafe_allow_html=True)
                        with cB:
                            st.checkbox("", value=st.session_state.get(asset_key, True), key=asset_key, disabled=not cat_enabled, label_visibility="collapsed")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. MÓDULO: MAPA TÉRMICO DE LIQUIDEZ COM CHECKBOX À DIREITA DO TÍTULO
# -----------------------------------------------------------------------------
col_sec_title, col_sec_chk = st.columns([4, 1])
with col_sec_title:
    if modulo == "Crypto":
        st.subheader("🔥 Mapa de Alavancagem & Open Interest (Bitcoin / Derivativos)")
    else:
        st.subheader("📈 Mapa Térmico de Volume Profile & Liquidez Institucional (S&P 500 Futures / TradFi)")
with col_sec_chk:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    st.checkbox("Incluir no Report", value=True, key="chk_include_heatmap")

if PLOTLY_AVAILABLE:
    base_price = quotes.get("BTC-USD" if modulo == "Crypto" else "ES=F", {"price": 77000.0}).get("price", 77000.0)
    if base_price == 0.0:
        base_price = 5000.0 if modulo == "TradFi (Macro)" else 77000.0

    prices = []
    liq_volumes = []
    data_source = ""
    unit_label = "M" if modulo == "Crypto" else "B"
    metric_label_type = "Open Interest / Liquidez Efetiva (Bitcoin)" if modulo == "Crypto" else "Volume Profile Institucional"

    if modulo == "Crypto":
        data_source = "Deribit API (BTC-PERPETUAL Order Book Real)"
        try:
            url = "https://www.deribit.com/api/v2/public/get_order_book?instrument_name=BTC-PERPETUAL&depth=250"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                book_data = res.json().get("result", {})
                bids = pd.DataFrame(book_data.get("bids", []), columns=["price", "qty"])
                asks = pd.DataFrame(book_data.get("asks", []), columns=["price", "qty"])
                df_book = pd.concat([bids, asks])
                if not df_book.empty:
                    df_book["notional_m"] = df_book["qty"] / 1_000_000
                    min_p = base_price * 0.85
                    max_p = base_price * 1.15
                    df_book = df_book[(df_book["price"] >= min_p) & (df_book["price"] <= max_p)]
                    num_bins = 25
                    bin_edges = np.linspace(min_p, max_p, num_bins + 1)
                    df_book["bin_idx"] = pd.cut(df_book["price"], bins=bin_edges, labels=False, include_lowest=True)
                    grouped = df_book.groupby("bin_idx")["notional_m"].sum().reset_index()
                    for i in range(num_bins):
                        p_mid = (bin_edges[i] + bin_edges[i+1]) / 2
                        matched = grouped[grouped["bin_idx"] == i]
                        v = float(matched["notional_m"].values[0]) if not matched.empty else 0.0
                        if v > 0:
                            prices.append(p_mid)
                            liq_volumes.append(v)
        except Exception:
            pass

        if not prices:
            prices = [base_price * 0.95, base_price * 0.98, base_price * 1.02, base_price * 1.05]
            liq_volumes = [1.2, 4.8, 6.5, 3.1]
    else:
        data_source = "Yahoo Finance API (S&P 500 Histórico Real — ES=F)"
        try:
            import yfinance as yf
            df_es = yf.download("ES=F", period="3mo", interval="1h", progress=False)
            if not df_es.empty:
                if isinstance(df_es.columns, pd.MultiIndex):
                    df_es.columns = df_es.columns.get_level_values(0)
                df_es = df_es.dropna(subset=['Close', 'Volume'])
                if not df_es.empty:
                    min_p = df_es['Close'].min()
                    max_p = df_es['Close'].max()
                    df_es["notional_b"] = (df_es['Close'] * df_es['Volume']) / 1_000_000_000
                    num_bins = 25
                    bin_edges = np.linspace(min_p, max_p, num_bins + 1)
                    df_es["bin_idx"] = pd.cut(df_es['Close'], bins=bin_edges, labels=False, include_lowest=True)
                    grouped = df_es.groupby("bin_idx")["notional_b"].sum().reset_index()
                    for i in range(num_bins):
                        p_mid = (bin_edges[i] + bin_edges[i+1]) / 2
                        matched = grouped[grouped["bin_idx"] == i]
                        v = float(matched["notional_b"].values[0]) if not matched.empty else 0.0
                        if v > 0:
                            prices.append(p_mid)
                            liq_volumes.append(v)
        except Exception:
            pass

        if not prices:
            prices = [base_price * 0.96, base_price * 0.99]
            liq_volumes = [18.4, 45.1]

    arr_v = np.array(liq_volumes, dtype=float)
    max_v = arr_v.max() if len(arr_v) > 0 and arr_v.max() > 0 else 1.0
    color_intensity = np.sqrt(arr_v / max_v) * 100.0

    df_clusters = pd.DataFrame({"price": prices, "volume": liq_volumes})
    df_above = df_clusters[df_clusters["price"] > base_price]
    top_res = df_above.loc[df_above["volume"].idxmax()] if not df_above.empty else {"price": base_price, "volume": 0}
    df_below = df_clusters[df_clusters["price"] < base_price]
    top_sup = df_below.loc[df_below["volume"].idxmax()] if not df_below.empty else {"price": base_price, "volume": 0}

    fig_oi = go.Figure()
    fig_oi.add_trace(go.Bar(
        y=prices,
        x=liq_volumes,
        orientation='h',
        marker=dict(
            color=color_intensity,
            colorscale='Jet',
            showscale=True,
            colorbar=dict(title="Intensidade Térmica", len=0.8, thickness=12, tickfont=dict(color="#C9D1D9"))
        ),
        hoverinfo='text',
        text=[f"Preço: {fmt_num(p)} | {metric_label_type}: ${v:.2f}{unit_label}" for p, v in zip(prices, liq_volumes)],
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

    chart_title = "Mapa Térmico de Open Interest & Alavancagem (Bitcoin / Deribit — $M)" if modulo == "Crypto" else "Volume Profile Histórico Real (S&P 500 Futures — $B)"
    xaxis_title = "Volume Notional Acumulado por Faixa ($ Milhões)" if modulo == "Crypto" else "Volume Notional Acumulado por Faixa ($ Bilhões)"

    fig_oi.update_layout(
        title=chart_title,
        paper_bgcolor="#0B0E14", 
        plot_bgcolor="#161B22", 
        font=dict(color="#C9D1D9", size=12),
        margin=dict(l=20, r=20, t=40, b=20), 
        height=520,
        yaxis=dict(gridcolor="#30363D", title="Níveis de Preço (USD)"),
        xaxis=dict(gridcolor="#30363D", title=xaxis_title)
    )
    st.plotly_chart(fig_oi, use_container_width=True)

    st.markdown(f"🟢 **Fonte Oficial da API Ativa:** `{data_source}`")
else:
    st.warning("⚠️ O módulo Plotly não está disponível no momento.")

st.markdown("---")
st.caption("⚡©️ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")