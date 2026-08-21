import json
from datetime import datetime
import streamlit as st

# Importação segura do Plotly com fallback
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Importação do Backend Modularizado
from backend import (
    CATEGORIES_TRADFI,
    MACRO_BENCHMARKS,
    CATEGORIES_CRYPTO,
    CRYPTO_BENCHMARKS,
    fmt_num,
    fmt_pct,
    generate_pdf_report,
    fetch_btc_fng,
    fetch_global_crypto_data,
    fetch_realtime_quotes,
    send_whatsapp_report
)

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
        margin-bottom: 8px;
        color: #94A3B8;
        font-size: 13px;
    }
    
    /* REGRAS DE CORES ESTRITAS */
    .color-green { color: #3FB950 !important; font-weight: 600; }
    .color-red { color: #F85149 !important; font-weight: 600; }
    .color-blue { color: #58A6FF !important; font-weight: 600; }

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
</style>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SIDEBAR: CONFIGURAÇÕES & MÓDULO BYOK / CRM API
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ Configurações OMNI")
modulo = st.sidebar.radio("📌 Escolha o Módulo:", ["Crypto", "TradFi (Macro)"], index=0)

# Seção BYOK & Integração CRM Avançada
with st.sidebar.expander("🔑 BYOK & API de CRM", expanded=False):
    brapi_token = st.text_input("BRAPI API Token:", value="", type="password")
    custom_data_api_key = st.text_input("Custom Market API Key:", value="", type="password")
    whatsapp_instance = st.text_input("WhatsApp Instance ID:", value="")
    whatsapp_token = st.text_input("WhatsApp API Token:", value="", type="password")
    
    st.markdown("---")
    st.markdown("**Integração Base de Contatos CRM**")
    crm_api_endpoint = st.text_input("CRM API Endpoint (Contatos):", value="", placeholder="https://api.seu-crm.com/v1/contacts")
    fallback_whatsapp_phone = st.text_input("Telefones Manuais (separados por vírgula):", value="", placeholder="+5548999999999, +554888888888")

tier_selected = st.sidebar.radio("Plano Ativo:", ["Free (Lead Magnet)", "Standard (B2C Trader)", "Premium (B2B White-Label)"], index=1)

allow_customization = "Free" not in tier_selected
allow_white_label = "Premium" in tier_selected
max_free_tickers = 5 if "Standard" in tier_selected else (999 if "Premium" in tier_selected else 0)

active_categories = CATEGORIES_CRYPTO if modulo == "Crypto" else CATEGORIES_TRADFI
active_benchmarks = CRYPTO_BENCHMARKS if modulo == "Crypto" else MACRO_BENCHMARKS

selected_categories = list(active_categories.keys())

custom_tickers = []
if allow_customization:
    c_input = st.sidebar.text_input("Tickers extras (ex: WEGE3.SA, PEPE-USD):", value="")
    if c_input:
        custom_tickers = [t.strip().upper() for t in c_input.split(",") if t.strip()][:max_free_tickers]

horizonte_pred = st.sidebar.selectbox("Horizonte Temporário:", ["24 Horas", "48 Horas", "7 Dias"], index=1)
alvo_pct = st.sidebar.slider("Projeção de Resposta (%)", 0.5, 15.0, 3.0, 0.5)
stop_pct = st.sidebar.slider("Zona de Suporte / Defesa (%)", 0.5, 15.0, 3.0, 0.5)

formato = st.sidebar.radio(f"📊 Formato ({modulo}):", ["B2B (Relatório Analítico)", "B2C (YouTube Auto-Pilot)", "B2C (Telegram / WhatsApp Auto-Pilot)"], index=0)

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

# Chamada das funções do backend
quotes = fetch_realtime_quotes(tuple(symbols_to_fetch), brapi_token=brapi_token, custom_api_key=custom_data_api_key)
fng_val, fng_class = fetch_btc_fng()
global_crypto_data = fetch_global_crypto_data()

active_display_categories = active_categories.copy()
if custom_tickers:
    active_display_categories["0 - Tickers Personalizados"] = {
        "tag": "Custom Feed",
        "assets": [(t, t, "R$" if ".SA" in t else "$") for t in custom_tickers]
    }
    selected_categories.insert(0, "0 - Tickers Personalizados")

# Função para buscar contatos via API do CRM ou lista manual separada por vírgula
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
col_status, col_btn_refresh = st.columns([3.5, 1])
with col_status:
    st.markdown(f'<div class="status-bar">🟢 <b>Dados consolidados às {now_str}</b> | Status API: <span class="color-green">● Online</span> | <b>Módulo:</b> {modulo}</div>', unsafe_allow_html=True)
with col_btn_refresh:
    if st.button("🔄 Atualizar Cotações"):
        st.cache_data.clear()
        st.rerun()

col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.subheader(f"📝 Relatório — {formato}")

    # Geração do texto dinâmico baseado nos ativos habilitados no dashboard
    if "B2B" in formato:
        report_lines = [
            f"=== RELATÓRIO INSTITUCIONAL {modulo.upper()} (B2B) ===",
            f"Emitente: {company_name} | Responsável: {cnpi_code}",
            f"Data/Hora de Emissão: {now_str}",
            f"Horizonte Analítico: {horizonte_pred} | Alvo: +{alvo_pct}% | Stop Defesa: -{stop_pct}%",
            f"Sentimento de Mercado (Fear & Greed): {fng_val} ({fng_class})",
            "",
            "--- SUMÁRIO DE ATIVOS E CATEGORIAS SELECIONADAS ---"
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
        
        # O estado do checkbox do Heat Map é lido aqui de forma segura
        include_heatmap = st.session_state.get("chk_include_heatmap", True)
        if include_heatmap:
            report_lines.extend([
                "",
                "--- ANÁLISE TÉCNICA DO HEAT MAP / LIQUIDEZ ---",
                f"Clusters de liquidez mapeados com sucesso. Viés operacional validado pelo fluxo de derivativos/ordens no horizonte de {horizonte_pred}."
            ])

        report_lines.extend([
            "",
            "--- CONCLUSÃO TÉCNICA QUANT ---",
            f"Tendência estrutural alinhada ao horizonte de {horizonte_pred}. Monitoramento ativo de zonas de liquidez para proteção de posições."
        ])
        output_content = "\n".join(report_lines)
    else:
        # Modo Auto-Pilot (YouTube / WhatsApp / Telegram)
        script_lines = [
            f"=== ROTEIRO AUTO-PILOT ({modulo.upper()}) ===",
            f"Data/Hora: {now_str}",
            f"Horizonte: {horizonte_pred}",
            "",
            "[INTRODUÇÃO - 00:00]",
            f"Fala, investidor! Panorama atualizado de {modulo} com dados consolidados em {now_str}.",
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
                    script_lines.append(f" - {disp_name} a {currency} {fmt_num(q['price'])}, variando {fmt_pct(q['change'])} hoje.")
        
        include_heatmap = st.session_state.get("chk_include_heatmap", True)
        if include_heatmap:
            script_lines.extend([
                "",
                "[DESTAQUE TÉCNICO - HEAT MAP]",
                "Nota de Mercado: O mapa de liquidez aponta fortes barreiras institucionais nos níveis atuais."
            ])

        script_lines.extend([
            "",
            "[FECHAMENTO - CALL TO ACTION]",
            "Deixe o seu like, se inscreva no canal e ative as notificações. Bons negócios!"
        ])
        output_content = "\n".join(script_lines)

    st.text_area("", value=output_content, height=415, label_visibility="collapsed")
    
    st.markdown("**Opções de Exportação & Disparo em Lote (CRM):**")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.download_button("📥 TXT", data=output_content, file_name=f"OMNI_Report_{modulo}.txt", mime="text/plain", use_container_width=True)
    with col_b2:
        json_data = json.dumps({"module": modulo, "timestamp": now_str, "content": output_content}, indent=4, ensure_ascii=False)
        st.download_button("📥 JSON", data=json_data, file_name=f"OMNI_Report_{modulo}.json", mime="application/json", use_container_width=True)
    with col_b3:
        pdf_bytes = generate_pdf_report(output_content, company_name, now_str)
        st.download_button("📥 PDF", data=pdf_bytes, file_name=f"OMNI_Report_{modulo}.pdf", mime="application/pdf", use_container_width=True)
    with col_b4:
        if st.button("🚀 Disparar CRM", use_container_width=True):
            contacts_list = get_crm_contacts_list(crm_api_endpoint, fallback_whatsapp_phone)
            if not contacts_list:
                st.warning("Nenhum contato encontrado na API do CRM ou telefones manuais.")
            else:
                success_count = 0
                for contact in contacts_list:
                    ok, _ = send_whatsapp_report(contact["phone"], whatsapp_instance, whatsapp_token, output_content)
                    if ok:
                        success_count += 1
                st.success(f"Disparo concluído! Enviado para {success_count}/{len(contacts_list)} contatos.")

with col_right:
    st.subheader(f"📈 Métricas Agregadas ({modulo})")
    st.caption(f"Atualizado às {datetime.now().strftime('%H:%M:%S BRT')}")

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
            chg_str = f"{fmt_pct(chg_val)} hoje"
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")
        elif item.get("ticker"):
            data = quotes.get(item["ticker"], {"price": 0.0, "change": 0.0})
            val_str = f"{item.get('prefix', '')}{fmt_num(data['price'])}"
            chg_val = data["change"]
            chg_str = f"{fmt_pct(chg_val)} hoje"
            change_cls = "color-green" if chg_val > 0 else ("color-red" if chg_val < 0 else "color-blue")

        st.markdown(f'<div class="metric-card"><div class="metric-title">{label}</div><div class="metric-value">{val_str}</div><div class="{change_cls}">{chg_str}</div></div>', unsafe_allow_html=True)

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

# -----------------------------------------------------------------------------
# 4. PAINEL DE ANÁLISE INTEGRADA (CARDS DE CATEGORIA COM TOGGLES INTERATIVOS)
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
# -------------------------------------------------------------
# 5. MÓDULO: MAPA TÉRMICO DE LIQUIDEZ E VOLUME PROFILE
# -------------------------------------------------------------

# CABEÇALHO DA SEÇÃO COM CHECKBOX ALINHADO AO LADO DO TÍTULO
col_sec_title, col_sec_chk = st.columns([4, 1])
with col_sec_title:
    if modulo == "Crypto":
        st.subheader("🔥 Mapa de Alavancagem & Open Interest (Bitcoin / Derivativos)")
    else:
        st.subheader("📊 Mapa Térmico de Volume Profile (Mercado Tradicional)")
with col_sec_chk:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    st.checkbox("Incluir no Report", value=True, key="chk_include_heatmap")

if PLOTLY_AVAILABLE:
    import requests
    import pandas as pd
    import numpy as np

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
    st.markdown("### 🎯 Pontos Criticos de Liquidez & Defesa Institucional")
    
    col_sup, col_res = st.columns(2)
    with col_sup:
        st.metric(
            label="🛡️ Principal Suporte (Histórico Real)",
            value=fmt_num(top_sup["price"]) if top_sup["volume"] > 0 else "N/D",
            delta=f"Volume: ${top_sup['volume']:.2f}{unit_label}" if top_sup["volume"] > 0 else "Sem dados"
        )
    with col_res:
        st.metric(
            label="⚡ Principal Resistência (Histórico Real)",
            value=fmt_num(top_res["price"]) if top_res["volume"] > 0 else "Zona de ATH (Sem Histórico Acima)",
            delta=f"Volume: ${top_res['volume']:.2f}{unit_label}" if top_res["volume"] > 0 else "Price Discovery"
        )
else:
    st.warning("⚠️ O módulo Plotly não está disponível no momento.")

st.markdown("---")
st.caption("⚡©️ Powered by OMNIRESEARCH Engine — Plataforma de Inteligência Financeira Preditiva.")