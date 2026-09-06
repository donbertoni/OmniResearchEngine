import base64
import json
from datetime import datetime, timezone
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from backend import CATEGORIES_CRYPTO, MACRO_BENCHMARKS, CRYPTO_BENCHMARKS, fetch_realtime_quotes, fetch_btc_fng, fetch_global_crypto_data

st.set_page_config(page_title="OMNI Research Engine", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

TRADFI = {
"1 - Bancos e Seguradoras": [("Itaú Unibanco", "ITUB4.SA"), ("Banco do Brasil", "BBAS3.SA"), ("Bradesco PN", "BBDC4.SA"), ("BB Seguridade", "BBSE3.SA")],
"2 - Energia": [("Petrobras PN", "PETR4.SA"), ("Petróleo Rio", "PRIO3.SA"), ("Equatorial", "EQTL3.SA"), ("CPFL Energia", "CPFE3.SA")],
"3 - Tech": [("Totvs", "TOTVS3.SA"), ("NVIDIA Corp", "NVDA"), ("Apple Inc", "AAPL"), ("Microsoft", "MSFT")],
"4 - Commodities": [("Vale ON", "VALE3.SA"), ("Gerdau", "GGBR4.SA"), ("Cemig", "CMIG4.SA"), ("Klabin", "KLBN11.SA")],
"5 - Varejo": [("Assaí", "ASAI3.SA"), ("Lojas Renner", "LREN3.SA"), ("Magazine Luiza", "MGLU3.SA"), ("RaiaDrogasil", "RADL3.SA")],
"6 - Logística e Infra.": [("Rumo", "RAIL3.SA"), ("Weg", "WEGE3.SA"), ("CCR", "CCRO3.SA"), ("Embraer", "EMBR3.SA")],
"7 - Agro e Indústria": [("SLC Agrícola", "SLCE3.SA"), ("BRF", "BRFS3.SA"), ("Ambev", "ABEV3.SA"), ("JBS", "JBSS3.SA")],
"8 - FIIs e Imobiliário": [("HGLG11", "HGLG11.SA"), ("KNRI11", "KNRI11.SA"), ("XPLG11", "XPLG11.SA"), ("MXRF11", "MXRF11.SA")],
}

def categories(module):
    if module == "tradfi": return list(TRADFI.items())
    return [(name, [(a[0], a[1]) for a in data["assets"]]) for name, data in CATEGORIES_CRYPTO.items()]

def heatmap(module, quotes):
    timestamp = datetime.now(timezone.utc).isoformat()
    if module == "crypto":
        base = float(quotes.get("BTC-USD", {"price": 77000}).get("price") or 77000)
        prices, volumes, source = [], [], "Deribit API (BTC-PERPETUAL order book)"
        try:
            res = requests.get("https://www.deribit.com/api/v2/public/get_order_book?instrument_name=BTC-PERPETUAL&depth=250", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
            book = res.json().get("result", {}) if res.ok else {}
            rows = book.get("bids", []) + book.get("asks", [])
            if rows:
                df = pd.DataFrame(rows, columns=["price", "qty"]); df = df[(df.price >= base*.85) & (df.price <= base*1.15)].copy(); df["notional"] = df.qty / 1_000_000
                bins = pd.cut(df.price, bins=25); grouped = df.groupby(bins, observed=False).notional.sum()
                for interval, value in grouped.items():
                    if value > 0: prices.append(float(interval.mid)); volumes.append(float(value))
        except Exception: pass
        if not prices: prices = [base*.95, base*.98, base*1.02, base*1.05]; volumes = [1.2, 4.8, 6.5, 3.1]
        return {"module":module,"title":"Leverage & Open Interest / BTC-PERPETUAL","prices":prices,"volumes":volumes,"unit":"M","basePrice":base,"source":source,"timestamp":timestamp,"note":"Clusters derived from the Deribit BTC perpetual order book; fallback levels are shown only when the provider is unavailable."}
    base = float(quotes.get("ES=F", {"price": 5000}).get("price") or 5000)
    prices, volumes, source = [], [], "Yahoo Finance API (ES=F historical volume profile)"
    try:
        import yfinance as yf
        df = yf.download("ES=F", period="3mo", interval="1h", progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            df = df.dropna(subset=["Close", "Volume"]); df["notional"] = df["Close"] * df["Volume"] / 1_000_000_000
            bins = pd.cut(df["Close"], bins=25); grouped = df.groupby(bins, observed=False)["notional"].sum()
            for interval, value in grouped.items():
                if value > 0: prices.append(float(interval.mid)); volumes.append(float(value))
    except Exception: pass
    if not prices: prices = [base*.96, base*.99]; volumes = [18.4, 45.1]
    return {"module":module,"title":"Volume Profile & Institutional Liquidity / ES=F","prices":prices,"volumes":volumes,"unit":"B","basePrice":base,"source":source,"timestamp":timestamp,"note":"Clusters derived from the ES=F historical volume profile; fallback levels are shown only when the provider is unavailable."}

@st.cache_data(ttl=60, show_spinner=False)
def build_overview(module):
    cats = categories(module); symbols = [s for _, aa in cats for _, s in aa]
    benchmarks = MACRO_BENCHMARKS if module == "tradfi" else CRYPTO_BENCHMARKS
    symbols += [x["ticker"] for x in benchmarks if x.get("ticker")]
    symbols = tuple(dict.fromkeys(symbols))
    try: quotes = fetch_realtime_quotes(symbols, brapi_token="")
    except Exception: quotes = {s: {"price":0.0,"change":0.0} for s in symbols}
    now = datetime.now(timezone.utc).isoformat(); assets=[]
    for _, aa in cats:
        for name, symbol in aa:
            q=quotes.get(symbol, {"price":0.0,"change":0.0}); p=float(q.get("price",0) or 0)
            assets.append({"name":name,"symbol":symbol,"price":p,"changePercent":float(q.get("change",0) or 0),"assetClass":"crypto" if "-USD" in symbol else "equity","source":"Yahoo Finance / BRAPI","dataStatus":"live" if p else "unavailable","isStale":not bool(p),"timestamp":now,"sparkline":[]})
    metrics=[]
    if module == "crypto":
        fng, fng_class = fetch_btc_fng(); glob = fetch_global_crypto_data()
    for item in benchmarks:
        if item.get("type") == "fng_api": metrics.append({"label":item["label"],"value":fng,"change":f"Sentiment: {fng_class}","changeValue":1 if fng_class=="Greed" else -1,"source":"Alternative.me"})
        elif item.get("type") == "global_api":
            key=item.get("sub_key"); val=glob["btc_d_val"] if key=="btc_d" else glob["usdt_d_val"]; ch=glob["btc_d_chg"] if key=="btc_d" else glob["usdt_d_chg"]; metrics.append({"label":item["label"],"value":val,"change":f"{ch:+.2f}%","changeValue":ch,"source":"CoinGecko"})
        else:
            q=quotes.get(item["ticker"], {"price":0.0,"change":0.0}); ch=float(q.get("change",0) or 0); p=float(q.get("price",0) or 0); metrics.append({"label":item["label"],"value":f"{item.get('prefix','')}{p:,.2f}" if p else "NO DATA","change":f"{ch:+.2f}%","changeValue":ch,"source":"Yahoo Finance"})
    available=[a for a in assets if a["price"]>0]
    return {"module":module,"asOf":now,"source":"Yahoo Finance / BRAPI / Deribit","dataStatus":"live" if available else "unavailable","isStale":not bool(available),"assets":assets,"metrics":metrics,"kpis":{"advancing":sum(a["changePercent"]>0 for a in available),"declining":sum(a["changePercent"]<0 for a in available),"total":len(assets),"available":len(available)},"heatmap":heatmap(module,quotes),"errors":[]}

bootstrap = {"tradfi":build_overview("tradfi"),"crypto":build_overview("crypto")}
html = r"""﻿<!doctype html>
<html lang="pt-BR" data-theme="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OMNI Research Engine | Market Intelligence</title>
    <style>
      @import url("https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap");

      :root {
        color-scheme: dark;
        --bg: #02050d;
        --bg-2: #07111e;
        --panel: rgba(8, 20, 33, 0.78);
        --panel-solid: #0a1523;
        --panel-soft: rgba(15, 32, 48, 0.58);
        --line: rgba(100, 116, 139, 0.34);
        --line-strong: rgba(103, 232, 249, 0.34);
        --text: #e8f3f7;
        --muted: #8293a1;
        --muted-2: #526475;
        --cyan: #67e8f9;
        --cyan-strong: #22d3ee;
        --green: #6ee7b7;
        --red: #fb7185;
        --amber: #fde68a;
        --purple: #d8b4fe;
        --radius: 5px;
        --shadow-cyan: 0 0 55px -23px rgba(34, 211, 238, 0.8);
      }

      [data-theme="light"] {
        color-scheme: light;
        --bg: #e8f0f2;
        --bg-2: #f8fbfb;
        --panel: rgba(255, 255, 255, 0.88);
        --panel-solid: #ffffff;
        --panel-soft: rgba(236, 246, 247, 0.9);
        --line: rgba(15, 54, 67, 0.18);
        --line-strong: rgba(8, 145, 178, 0.42);
        --text: #122733;
        --muted: #526b78;
        --muted-2: #738b95;
        --cyan: #087f9b;
        --cyan-strong: #0891b2;
        --green: #047857;
        --red: #be123c;
        --amber: #a16207;
        --purple: #7e22ce;
        --shadow-cyan: 0 0 45px -22px rgba(8, 145, 178, 0.5);
      }

      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        min-width: 320px;
        color: var(--text);
        background:
          radial-gradient(circle at 12% 0%, rgba(6, 182, 212, .10), transparent 28%),
          linear-gradient(rgba(15, 23, 42, .25) 1px, transparent 1px),
          linear-gradient(90deg, rgba(15, 23, 42, .25) 1px, transparent 1px),
          var(--bg);
        background-size: auto, 44px 44px, 44px 44px;
        font-family: "Space Grotesk", sans-serif;
      }
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        z-index: 20;
        pointer-events: none;
        opacity: .12;
        background: repeating-linear-gradient(0deg, transparent 0, transparent 3px, rgba(34, 211, 238, .045) 4px);
      }
      button, input, select, textarea { font: inherit; }
      button { cursor: pointer; }
      button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible {
        outline: 2px solid var(--cyan-strong);
        outline-offset: 3px;
      }
      .mono, .eyebrow, .metric-value, .data-table { font-family: "IBM Plex Mono", monospace; }
      .eyebrow {
        color: var(--muted-2);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: .18em;
        text-transform: uppercase;
      }
      .app-shell {
        display: grid;
        grid-template-columns: 254px minmax(0, 1fr);
        min-height: 100vh;
      }
      aside {
        position: sticky;
        top: 0;
        align-self: start;
        height: 100vh;
        overflow-y: auto;
        padding: 22px 16px;
        border-right: 1px solid rgba(103, 232, 249, .16);
        background: linear-gradient(180deg, rgba(3, 11, 20, .92), rgba(4, 13, 22, .68));
        backdrop-filter: blur(18px);
      }
      .brand {
        display: flex;
        gap: 11px;
        align-items: center;
        padding: 0 6px 22px;
        border-bottom: 1px solid var(--line);
      }
      .brand-mark {
        display: grid;
        width: 38px;
        height: 38px;
        place-items: center;
        color: var(--cyan);
        border: 1px solid rgba(103, 232, 249, .55);
        border-radius: 50%;
        box-shadow: var(--shadow-cyan), inset 0 0 18px rgba(34, 211, 238, .08);
      }
      .brand-mark::before { content: "O"; font: 600 22px "IBM Plex Mono"; }
      .brand-name { font-size: 14px; font-weight: 700; letter-spacing: -.02em; }
      .brand-name span { color: var(--cyan); }
      .brand-subtitle { margin-top: 3px; color: var(--muted-2); font-size: 8px; letter-spacing: .08em; text-transform: uppercase; }
      .side-section { padding: 20px 6px 0; }
      .side-label { display: block; margin-bottom: 9px; color: var(--muted-2); font: 600 9px "IBM Plex Mono"; letter-spacing: .14em; text-transform: uppercase; }
      .side-control, .side-select, .side-input {
        width: 100%;
        min-height: 36px;
        padding: 9px 10px;
        color: var(--text);
        border: 1px solid var(--line);
        border-radius: 3px;
        background: rgba(2, 8, 16, .52);
      }
      .side-select option { background: #07111e; }
      .side-control:hover, .side-select:hover, .side-input:hover { border-color: var(--line-strong); }
      .radio-group { display: grid; gap: 5px; }
      .radio-option {
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 8px 9px;
        color: var(--muted);
        border: 1px solid transparent;
        transition: .2s ease;
      }
      .radio-option:has(input:checked) { color: var(--cyan); border-color: rgba(103, 232, 249, .28); background: rgba(34, 211, 238, .07); }
      .radio-option input, .check-row input { accent-color: var(--cyan-strong); }
      .check-list { display: grid; gap: 9px; }
      .check-row { display: flex; gap: 8px; align-items: center; color: var(--muted); font-size: 12px; }
      .side-button, .button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 36px;
        padding: 8px 12px;
        color: var(--cyan);
        border: 1px solid rgba(103, 232, 249, .34);
        border-radius: 3px;
        background: rgba(34, 211, 238, .07);
        font: 600 10px "IBM Plex Mono";
        letter-spacing: .04em;
        transition: .2s ease;
      }
      .side-button { width: 100%; margin-top: 10px; }
      .side-button:hover, .button:hover { color: #d9fbff; border-color: var(--cyan); background: rgba(34, 211, 238, .14); box-shadow: var(--shadow-cyan); transform: translateY(-1px); }
      .button.secondary { color: var(--muted); border-color: var(--line); background: transparent; }
      .button.green { color: var(--green); border-color: rgba(110, 231, 183, .34); background: rgba(16, 185, 129, .07); }
      .button.amber { color: var(--amber); border-color: rgba(253, 230, 138, .32); background: rgba(245, 158, 11, .06); }
      main { min-width: 0; }
      .topbar {
        position: sticky;
        top: 0;
        z-index: 10;
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: center;
        padding: 14px 30px;
        border-bottom: 1px solid rgba(103, 232, 249, .15);
        background: rgba(2, 7, 15, .80);
        backdrop-filter: blur(18px);
      }
      .topbar-title { color: var(--text); font-size: 13px; font-weight: 600; }
      .topbar-title span { color: var(--cyan); }
      .topbar-meta { display: flex; gap: 18px; align-items: center; color: var(--muted); font: 10px "IBM Plex Mono"; }
      .status-dot { display: inline-block; width: 7px; height: 7px; margin-right: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); }
      .status-dot.stale { background: var(--amber); box-shadow: 0 0 10px var(--amber); }
      .workspace { width: min(1440px, 100%); margin: 0 auto; padding: 28px 30px 50px; }
      .page-heading { display: flex; justify-content: space-between; gap: 20px; align-items: end; margin-bottom: 19px; }
      h1, h2, h3, p { margin: 0; }
      h1 { font-size: clamp(32px, 5vw, 63px); line-height: .92; letter-spacing: -.06em; }
      h1 span { color: var(--cyan); }
      .page-heading p { max-width: 570px; margin-top: 11px; color: var(--muted); font-size: 13px; line-height: 1.6; }
      .heading-actions { display: flex; flex-wrap: wrap; gap: 7px; justify-content: flex-end; }
      .status-strip { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 9px; margin-bottom: 16px; }
      .status-pill { min-height: 38px; padding: 10px 12px; color: var(--muted); border: 1px solid var(--line); background: var(--panel); font: 10px "IBM Plex Mono"; }
      .status-pill strong { color: var(--text); font-weight: 500; }
      .status-pill.live { color: var(--green); border-color: rgba(110, 231, 183, .35); }
      .dashboard-grid { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(300px, .8fr); gap: 14px; align-items: start; }
      .panel {
        position: relative;
        overflow: hidden;
        padding: 21px;
        border: 1px solid var(--line);
        border-radius: var(--radius);
        background: linear-gradient(140deg, var(--panel), rgba(2, 8, 16, .64));
        box-shadow: inset 0 1px rgba(148, 163, 184, .06);
      }
      .panel::after { content: ""; position: absolute; top: 0; right: 12%; width: 90px; height: 1px; background: linear-gradient(90deg, transparent, var(--cyan), transparent); opacity: .7; }
      .panel.cyan { border-color: rgba(103, 232, 249, .3); box-shadow: var(--shadow-cyan), inset 0 1px rgba(103, 232, 249, .10); }
      .panel.purple { border-color: rgba(216, 180, 254, .25); box-shadow: 0 0 55px -25px rgba(168, 85, 247, .65); }
      .panel-heading { display: flex; justify-content: space-between; gap: 15px; align-items: start; margin-bottom: 17px; }
      .panel-heading h2 { margin-top: 6px; font-size: 21px; letter-spacing: -.045em; }
      .panel-heading p { max-width: 360px; color: var(--muted); font-size: 11px; line-height: 1.55; text-align: right; }
      .panel-tools { display: flex; flex-wrap: wrap; gap: 7px; justify-content: flex-end; }
      .section-rule { height: 1px; margin: 15px 0; background: linear-gradient(90deg, rgba(103, 232, 249, .35), rgba(71, 85, 105, .15), transparent); }
      .delivery-box { min-height: 280px; padding: 17px; border: 1px dashed rgba(103, 232, 249, .34); background: rgba(2, 8, 16, .42); }
      .delivery-box textarea { width: 100%; min-height: 218px; padding: 14px; resize: vertical; color: #c9f8ff; border: 1px solid rgba(71, 85, 105, .65); border-radius: 3px; background: rgba(2, 6, 13, .85); font: 11px/1.65 "IBM Plex Mono"; }
      .delivery-box textarea:focus { border-color: var(--cyan); outline: none; box-shadow: 0 0 0 3px rgba(34, 211, 238, .08); }
      .delivery-footer { display: grid; grid-template-columns: repeat(4, 1fr); gap: 7px; margin-top: 9px; }
      .metric-list { display: grid; gap: 8px; }
      .metric-card { position: relative; padding: 13px; border: 1px solid var(--line); background: rgba(6, 16, 27, .7); transition: .2s ease; }
      .metric-card:hover { border-color: rgba(103, 232, 249, .5); transform: translateX(2px); }
      .metric-top { display: flex; justify-content: space-between; gap: 10px; color: var(--muted); font-size: 10px; }
      .source { padding: 3px 5px; color: var(--muted-2); border: 1px solid var(--line); font: 8px "IBM Plex Mono"; }
      .data-meta { margin-top: 7px; color: var(--muted-2); font: 8px/1.45 "IBM Plex Mono"; }
      .asset-row .data-meta { grid-column: 1 / -1; }
      .data-meta.stale { color: var(--amber); }
      .stale-note { margin-top: 7px; padding: 6px 7px; color: var(--amber); border-left: 2px solid var(--amber); background: rgba(245, 158, 11, .06); font: 8px/1.45 "IBM Plex Mono"; }
      .data-status { display: inline-block; margin-right: 5px; color: var(--green); }
      .data-status.cached, .data-status.demo { color: var(--amber); }
      .api-error { margin-bottom: 12px; padding: 10px 12px; color: var(--red); border: 1px solid rgba(251, 113, 133, .4); background: rgba(190, 18, 60, .08); font: 10px/1.5 "IBM Plex Mono"; }
      .loading-state { padding: 22px; color: var(--muted); border: 1px dashed var(--line); font: 10px "IBM Plex Mono"; }
      .metric-value { margin: 5px 0 3px; color: var(--text); font-size: 20px; font-weight: 600; }
      /* Alignment-only adjustment: preserve card density and enlarge only the report body. */
      .panel.cyan .delivery-box { min-height: 500px; }
      .panel.cyan .delivery-box textarea { min-height: 438px; }

      .positive { color: var(--green) !important; }
      .negative { color: var(--red) !important; }
      .neutral { color: var(--cyan) !important; }
      .integrated, .agents, .heatmap { grid-column: 1 / -1; }
      .category-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
      .category-card { min-width: 0; padding: 14px; border: 1px solid var(--line); background: rgba(7, 18, 29, .62); transition: .2s ease; }
      .category-card:hover { border-color: rgba(103, 232, 249, .42); background: rgba(34, 211, 238, .05); }
      .category-top { display: flex; justify-content: space-between; gap: 8px; align-items: center; margin-bottom: 11px; }
      .category-name { overflow: hidden; color: var(--text); font-size: 12px; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
      .asset-row { display: grid; grid-template-columns: 1fr auto; gap: 6px; padding: 8px 0; border-top: 1px solid rgba(71, 85, 105, .28); }
      .asset-name { color: var(--muted); font-size: 10px; }
      .asset-detail { display: flex; gap: 7px; justify-content: flex-end; align-items: center; color: var(--text); font: 10px "IBM Plex Mono"; }
      .agent-tabs { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 13px; }
      .tab { padding: 8px 10px; color: var(--muted); border: 1px solid var(--line); background: transparent; font: 9px "IBM Plex Mono"; text-transform: uppercase; }
      .tab.active, .tab:hover { color: var(--cyan); border-color: rgba(103, 232, 249, .5); background: rgba(34, 211, 238, .08); }
      .agent-content { min-height: 205px; padding: 16px; border: 1px solid var(--line); background: rgba(2, 8, 16, .45); }
      .agent-content h3 { margin-bottom: 8px; font-size: 17px; letter-spacing: -.04em; }
      .agent-content p { max-width: 780px; color: var(--muted); font-size: 12px; line-height: 1.6; }
      .agent-controls { display: grid; grid-template-columns: repeat(2, minmax(180px, 1fr)); gap: 9px; margin: 17px 0; }
      .field label { display: block; margin-bottom: 6px; color: var(--muted-2); font: 9px "IBM Plex Mono"; text-transform: uppercase; }
      .field input, .field select { width: 100%; min-height: 35px; padding: 8px; color: var(--text); border: 1px solid var(--line); border-radius: 3px; background: var(--panel-solid); }
      .field select[multiple] { min-height: 120px; }
      .field small { display: block; margin-top: 6px; color: var(--muted-2); font: 9px/1.45 "IBM Plex Mono"; }
      .calibration-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 14px; }
      .agent-kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
      .mini-kpi { padding: 11px; border-left: 2px solid var(--cyan); background: rgba(34, 211, 238, .05); }
      .mini-kpi .eyebrow { font-size: 8px; }
      .mini-kpi strong { display: block; margin-top: 6px; font: 600 16px "IBM Plex Mono"; }
      .data-table { width: 100%; border-collapse: collapse; color: var(--muted); font-size: 10px; }
      .data-table th, .data-table td { padding: 8px 5px; text-align: left; border-top: 1px solid rgba(71, 85, 105, .28); }
      .data-table th { color: var(--muted-2); font-size: 8px; letter-spacing: .12em; text-transform: uppercase; }
      .heatmap-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
      .heatmap-visual { min-height: 250px; padding: 17px; border: 1px solid var(--line); background: linear-gradient(180deg, rgba(8, 29, 45, .75), rgba(2, 6, 16, .72)); }
      .bar-row { display: grid; grid-template-columns: 70px 1fr 50px; gap: 8px; align-items: center; margin: 13px 0; color: var(--muted); font: 10px "IBM Plex Mono"; }
      .bar-track { height: 8px; overflow: hidden; border: 1px solid rgba(103, 232, 249, .18); background: rgba(15, 23, 42, .8); }
      .bar { height: 100%; background: linear-gradient(90deg, var(--cyan-strong), var(--purple)); box-shadow: 0 0 14px rgba(34, 211, 238, .7); }
      .heatmap-note { padding: 15px; border: 1px solid rgba(216, 180, 254, .25); color: var(--muted); background: rgba(168, 85, 247, .04); font-size: 12px; line-height: 1.6; }
      .heatmap-note strong { color: var(--purple); }
      .footer { margin-top: 24px; padding-top: 15px; color: var(--muted-2); border-top: 1px solid var(--line); font: 9px "IBM Plex Mono"; text-align: center; letter-spacing: .1em; text-transform: uppercase; }
      .toast { position: fixed; right: 22px; bottom: 22px; z-index: 50; max-width: 350px; padding: 13px 15px; color: var(--text); border: 1px solid rgba(103, 232, 249, .45); background: rgba(2, 8, 16, .94); box-shadow: var(--shadow-cyan); font: 11px/1.5 "IBM Plex Mono"; opacity: 0; transform: translateY(12px); pointer-events: none; transition: .25s ease; }
      .toast.show { opacity: 1; transform: translateY(0); }
      .modal-backdrop { position: fixed; inset: 0; z-index: 40; display: none; place-items: center; padding: 20px; background: rgba(1, 5, 13, .82); backdrop-filter: blur(10px); }
      .modal-backdrop.open { display: grid; }
      .modal { width: min(650px, 100%); max-height: calc(100dvh - 40px); overflow-y: auto; padding: 22px; border: 1px solid rgba(103, 232, 249, .35); background: linear-gradient(145deg, #0a1d2b, #030914); box-shadow: var(--shadow-cyan); }
      .modal-header { display: flex; justify-content: space-between; gap: 15px; padding-bottom: 14px; border-bottom: 1px solid var(--line); }
      .modal-header h2 { margin-top: 6px; font-size: 24px; letter-spacing: -.05em; }
      .close { color: var(--muted); border: 0; background: transparent; font-size: 22px; }
      .modal-body { padding-top: 17px; color: var(--muted); font-size: 12px; line-height: 1.7; }
      .hidden { display: none !important; }
      @media (max-width: 1100px) {
        .app-shell { grid-template-columns: 220px minmax(0, 1fr); }
        .category-grid { grid-template-columns: repeat(2, 1fr); }
      }
      @media (max-width: 800px) {
        .app-shell { display: block; }
        aside { position: relative; height: auto; border-right: 0; border-bottom: 1px solid rgba(103, 232, 249, .16); }
        .side-section { display: inline-block; width: 48%; vertical-align: top; padding-top: 15px; padding-right: 8px; }
        .topbar { position: relative; padding: 13px 17px; }
        .topbar-meta { display: flex; gap: 8px; font-size: 8px; }
        #clock { display: none; }
        #api-status { white-space: nowrap; }
        #theme-toggle { min-height: 32px; padding: 7px 8px; font-size: 8px; }
        .workspace { padding: 22px 16px 38px; }
        .page-heading { display: block; }
        .heading-actions { justify-content: flex-start; margin-top: 17px; }
        .status-strip, .dashboard-grid { grid-template-columns: 1fr; }
        .integrated, .agents, .heatmap { grid-column: auto; }
        .heatmap-grid { grid-template-columns: 1fr; }
      }
      @media (max-width: 520px) {
        .side-section { display: block; width: 100%; }
        .category-grid, .agent-kpis, .agent-controls { grid-template-columns: 1fr; }
        .calibration-grid { grid-template-columns: 1fr; }
        .delivery-footer { grid-template-columns: repeat(2, 1fr); }
        .panel { padding: 15px; }
        .panel-heading { display: block; }
        .panel-heading p { margin-top: 10px; text-align: left; }
        .panel-tools { justify-content: flex-start; margin-top: 11px; }
        .heading-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .heading-actions .button { width: 100%; }
        #health { grid-column: 1 / -1; }
        .status-pill { overflow-wrap: anywhere; }
        .modal-backdrop { padding: 8px; }
        .modal { max-height: calc(100dvh - 16px); padding: 15px; }
        .modal-header h2 { font-size: 19px; }
        .modal-body { font-size: 11px; }
        .asset-detail { font-size: 9px; }
      }
      @media print {
        body::before, aside, .topbar, .heading-actions, .side-section, .toast, .modal-backdrop { display: none !important; }
        body { background: white; color: #111; }
        .app-shell, .workspace { display: block; }
        .workspace { width: 100%; padding: 0; }
        .panel, .status-pill { color: #111; background: white; box-shadow: none; break-inside: avoid; }
      }
    </style>
  <script>window.__OMNI_BOOTSTRAP__=__OMNI_BOOTSTRAP_PLACEHOLDER__;</script></head>
  <body>
    <div class="app-shell">
      <aside aria-label="OMNI configuration">
        <div class="brand">
          <div class="brand-mark" aria-hidden="true"></div>
          <div>
            <div class="brand-name">OMNI<span>RESEARCH</span></div>
            <div class="brand-subtitle">Financial intelligence engine</div>
          </div>
        </div>

        <div class="side-section">
          <label class="side-label" id="language-label" for="language">Idioma / Language</label>
          <select id="language" class="side-select">
            <option value="PT">Português (BR)</option>
            <option value="EN">English (US)</option>
          </select>
        </div>

        <div class="side-section">
          <span class="side-label" id="module-label">Módulo / Module</span>
          <div class="radio-group">
            <label class="radio-option"><input type="radio" name="module" value="crypto" /> Crypto</label>
            <label class="radio-option"><input type="radio" name="module" value="tradfi" checked /> TradFi (Macro)</label>
          </div>
        </div>

        <div class="side-section">
          <span class="side-label" id="outputs-label">Formatos de saída</span>
          <div class="check-list">
            <label class="check-row"><input type="checkbox" id="format-b2b" checked /> B2B · Relatório analítico</label>
            <label class="check-row"><input type="checkbox" id="format-youtube" /> B2C · YouTube Auto-Pilot</label>
            <label class="check-row"><input type="checkbox" id="format-whatsapp" /> B2C · WhatsApp Auto-Pilot</label>
            <label class="check-row"><input type="checkbox" id="format-telegram" /> B2C · Telegram Auto-Pilot</label>
          </div>
           <button class="side-button" id="production">Acionar produção automática</button>
        </div>

        <div class="side-section">
          <span class="side-label" id="advanced-label">Configurações avançadas</span>
          <button class="side-button secondary config-button" data-config="automations">Automações</button>
          <button class="side-button secondary config-button" data-config="triggers">Gatilhos de report</button>
          <button class="side-button secondary config-button" data-config="calibration">Calibragem da engine</button>
        </div>

        <div class="side-section">
          <span class="side-label" id="plan-label">Plano ativo</span>
          <div class="mono" style="color:var(--green);font-size:11px">STANDARD</div>
          <div class="mono" style="color:var(--muted-2);font-size:9px;margin-top:4px">B2C TRADER / OBSERVER</div>
        </div>
      </aside>

      <main>
        <header class="topbar">
          <div class="topbar-title"><span>OMNI</span> / <span id="terminal-title">Market intelligence terminal</span></div>
          <div class="topbar-meta">
             <span id="api-status"><i class="status-dot"></i>API STATUS · CONNECTING</span>
            <span id="clock">--:--:-- BRT</span>
            <button class="button secondary" id="theme-toggle">LIGHT MODE</button>
          </div>
        </header>

        <div class="workspace">
          <section class="page-heading">
            <div>
              <div class="eyebrow" style="color:var(--cyan)">01 · Command center / live readout</div>
              <h1>OMNI Research<br /><span>Engine.</span></h1>
              <p id="page-description">Plataforma integrada de inteligência financeira com análise TradFi, módulo crypto, automações e arquitetura de agentes especializados.</p>
            </div>
            <div class="heading-actions">
              <button class="button" id="refresh">↻ REFRESH</button>
              <button class="button secondary" id="print">EXPORT PDF</button>
              <button class="button green" id="health">● ENGINE HEALTH 99.8%</button>
            </div>
          </section>

          <div class="status-strip">
             <div class="status-pill"><strong id="date-label">--</strong> · Market session / provider timestamp</div>
             <div class="status-pill live" id="auto-status"><span class="status-dot"></span><strong>Auto-Pilot</strong> · monitoring</div>
             <div class="status-pill">Sources · <strong id="source-label">CONNECTING</strong></div>
          </div>

          <div class="dashboard-grid">
            <section class="panel cyan">
              <div class="panel-heading">
                <div>
                  <div class="eyebrow" style="color:var(--cyan)">02 · Selected deliveries</div>
                  <h2 id="deliveries-title">Report production bay</h2>
                </div>
                 <p id="deliveries-description">Geração de relatórios e scripts a partir das cotações, benchmarks e seleções do dashboard.</p>
              </div>
              <div class="delivery-box">
                <div class="eyebrow" style="color:var(--cyan);margin-bottom:10px">INSTITUTIONAL REPORT · <span id="report-module">TRADFI (MACRO)</span> · B2B</div>
                 <textarea id="report" aria-label="Generated report" placeholder="Loading normalized provider data…"></textarea>
              </div>
              <div class="delivery-footer">
                <button class="button" data-export="TXT">↓ TXT</button>
                <button class="button" data-export="JSON">↓ JSON</button>
                <button class="button amber" data-export="PDF">↓ PDF</button>
                <button class="button secondary" id="crm-push">CRM PUSH</button>
              </div>
            </section>

            <section class="panel purple">
              <div class="panel-heading">
                <div>
                  <div class="eyebrow" style="color:var(--purple)">03 · Aggregated metrics</div>
                  <h2 id="metrics-title">TradFi (Macro)</h2>
                </div>
              </div>
               <div class="metric-list" id="metric-list"><div class="loading-state">Connecting to the market data service…</div></div>
            </section>

            <section class="panel integrated">
              <div class="panel-heading">
                <div>
                  <div class="eyebrow" style="color:var(--cyan)">04 · Integrated category panel</div>
                  <h2 id="integrated-title">Market map / monitored assets</h2>
                </div>
                <div class="panel-tools">
                  <button class="button secondary" id="select-all">SELECT ALL</button>
                  <button class="button secondary" id="clear-all">CLEAR</button>
                </div>
              </div>
              <div class="category-grid" id="category-grid"></div>
            </section>

            <section class="panel agents">
              <div class="panel-heading">
                <div>
                  <div class="eyebrow" style="color:var(--green)">05 · Specialized agent architecture</div>
                  <h2 id="agents-title">Signal orchestration layer</h2>
                </div>
                 <p id="agents-description">Agentes para predição, análise técnica, roteirização e direção de arte. Cada módulo está preparado para receber um serviço real.</p>
              </div>
              <div class="agent-tabs" role="tablist">
                <button class="tab active" data-agent="script">Scriptwriter Agent</button>
                <button class="tab" data-agent="predictive">Predictive Agent · ML</button>
                <button class="tab" data-agent="technical">Technical Analysis</button>
                <button class="tab" data-agent="art">Art Director AI</button>
              </div>
              <div class="agent-content" id="agent-content">
                <div class="eyebrow" style="color:var(--cyan)">Agent state · ready</div>
                <h3>Multi-format scriptwriter</h3>
                <p>Coleta preços, indicadores macro/crypto e sentimento para sintetizar roteiros direcionados para relatório institucional, WhatsApp, Telegram e YouTube.</p>
                <div class="agent-controls">
                  <div class="field"><label for="agent-asset">Ativo alvo para roteiro</label><select id="agent-asset"><option>BTC-USD</option><option>ES=F</option><option>ITUB4.SA</option><option>PETR4.SA</option></select></div>
                  <div class="field"><label for="agent-tone">Tom do roteiro</label><select id="agent-tone"><option>Institucional / B2B</option><option>Trader / HFT</option><option>Educacional / Retail</option></select></div>
                </div>
                <button class="button" id="run-agent">EXECUTAR AGENTE</button>
              </div>
            </section>

            <section class="panel heatmap">
              <div class="panel-heading">
                <div>
                  <div class="eyebrow" style="color:var(--amber)">06 · Liquidity intelligence module</div>
                 <h2 id="heatmap-title">Volume profile &amp; institutional liquidity</h2>
                </div>
                <div class="panel-tools"><span class="source">SOURCE · YAHOO FINANCE</span><button class="button secondary" id="heatmap-report">INCLUDE IN REPORT</button></div>
              </div>
              <div class="heatmap-grid">
                 <div class="heatmap-visual" id="heatmap-visual"><div class="loading-state">Waiting for a normalized price series…</div></div>
                 <div class="heatmap-note" id="heatmap-note"><div class="loading-state">Provider metadata will appear with the selected module.</div></div>
              </div>
            </section>
          </div>

          <div class="footer">OMNI Research Engine · Predictive financial intelligence · Data snapshots are for research purposes</div>
        </div>
      </main>
    </div>

    <div class="toast" id="toast" role="status" aria-live="polite"></div>
    <div class="modal-backdrop" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div class="modal">
        <div class="modal-header"><div><div class="eyebrow" style="color:var(--cyan)">Configuration surface</div><h2 id="modal-title">Advanced settings</h2></div><button class="close" id="modal-close" aria-label="Close">×</button></div>
        <div class="modal-body" id="modal-body">Configuration controls are ready to be connected to the Python backend.</div>
      </div>
    </div>

    <script>
       const DEFAULT_CATEGORIES = {
  tradfi: [
    ["1 - Bancos e Seguradoras", [["Itaú Unibanco", "ITUB4.SA"], ["Banco do Brasil", "BBAS3.SA"], ["Bradesco PN", "BBDC4.SA"], ["BB Seguridade", "BBSE3.SA"]]],
    ["2 - Energia", [["Petrobras PN", "PETR4.SA"], ["Petróleo Rio", "PRIO3.SA"], ["Equatorial", "EQTL3.SA"], ["CPFL Energia", "CPFE3.SA"]]],
    ["3 - Tech", [["Totvs", "TOTVS3.SA"], ["NVIDIA Corp", "NVDA"], ["Apple Inc", "AAPL"], ["Microsoft", "MSFT"]]],
    ["4 - Commodities", [["Vale ON", "VALE3.SA"], ["Gerdau", "GGBR4.SA"], ["Cemig", "CMIG4.SA"], ["Klabin", "KLBN11.SA"]]],
    ["5 - Varejo", [["Assaí", "ASAI3.SA"], ["Lojas Renner", "LREN3.SA"], ["Magazine Luiza", "MGLU3.SA"], ["RaiaDrogasil", "RADL3.SA"]]],
    ["6 - Logística e Infra.", [["Rumo", "RAIL3.SA"], ["Weg", "WEGE3.SA"], ["CCR", "CCRO3.SA"], ["Embraer", "EMBR3.SA"]]],
    ["7 - Agro e Indústria", [["SLC Agrícola", "SLCE3.SA"], ["BRF", "BRFS3.SA"], ["Ambev", "ABEV3.SA"], ["JBS", "JBSS3.SA"]]],
    ["8 - FIIs e Imobiliário", [["HGLG11", "HGLG11.SA"], ["KNRI11", "KNRI11.SA"], ["XPLG11", "XPLG11.SA"], ["MXRF11", "MXRF11.SA"]]]
  ],
  crypto: [
    ["1 - ETFs", [["IBIT (BlackRock)", "IBIT"], ["FBTC (Fidelity)", "FBTC"], ["ETHA (Ethereum)", "ETHA"], ["BITO (Futures)", "BITO"]]],
    ["2 - Treasury", [["MicroStrategy", "MSTR"], ["Marathon Digital", "MARA"], ["Riot Platforms", "RIOT"], ["Coinbase Global", "COIN"]]],
    ["3 - Mineração e Hashrate", [["CleanSpark", "CLSK"], ["Hut 8", "HUT"], ["Bitfarms", "BITF"], ["Iris Energy", "IREN"]]],
    ["4 - Volume Spot (24 hs)", [["BTCUSDT", "BTC-USD"], ["ETHUSDT", "ETH-USD"], ["SOLUSDT", "SOL-USD"], ["BNBUSDT", "BNB-USD"]]],
    ["5 - Volume Futuros (24 hs)", [["BTC Perp", "BTC-USD"], ["ETH Perp", "ETH-USD"], ["SOL Perp", "SOL-USD"], ["BNB Perp", "BNB-USD"]]],
    ["6 - Open Interest", [["BTC OI Base", "BTC-USD"], ["ETH OI Base", "ETH-USD"], ["SOL OI Base", "SOL-USD"], ["AVAX OI Base", "AVAX-USD"]]],
    ["7 - DeFi e Layer 1s", [["UNI (Uniswap)", "UNI7083-USD"], ["AAVE (Aave)", "AAVE-USD"], ["LINK (Chainlink)", "LINK-USD"], ["AVAX (Avalanche)", "AVAX-USD"]]],
    ["8 - Stablecoins", [["USDT / USD", "USDT-USD"], ["USDC / USD", "USDC-USD"], ["USDT / BRL", "BRL=X"], ["DAI / USD", "DAI-USD"]]]
  ]
};
const TRADFI_METRICS = [["S&P 500 INDEX", "SPX"], ["NASDAQ 100", "NDX"], ["VOLATILITY INDEX", "VIX"]];
      const CRYPTO_METRICS = [["BITCOIN", "BTC-USD"], ["ETHEREUM", "ETH-USD"], ["SOLANA", "SOL-USD"]];
      const $ = (selector) => document.querySelector(selector);
      const $$ = (selector) => Array.from(document.querySelectorAll(selector));
      const marketState = { data: null, error: null, loading: false, request: 0 };
       const configState = {
         categories: JSON.parse(localStorage.getItem("omni.categories") || "null") || structuredClone(DEFAULT_CATEGORIES),
         pools: JSON.parse(localStorage.getItem("omni.pools") || "null"),
         language: localStorage.getItem("omni.language") || "PT"
       };
       const categoriesForModule = () => configState.categories[currentModule()] || DEFAULT_CATEGORIES[currentModule()];
       const LANGUAGE_COPY = {
         PT: {
           module: "Módulo / Module", outputs: "Formatos de saída", advanced: "Configurações avançadas", plan: "Plano ativo",
           production: "Acionar produção automática", automations: "Automações", triggers: "Gatilhos de report", calibration: "Calibragem da engine",
           terminal: "Market intelligence terminal", description: "Plataforma integrada de inteligência financeira com análise TradFi, módulo crypto, automações e arquitetura de agentes especializados.",
           deliveries: "Report production bay", deliveriesDescription: "Geração de relatórios e scripts a partir das cotações, benchmarks e seleções do dashboard.",
           integrated: "Market map / monitored assets", agents: "Signal orchestration layer", agentsDescription: "Agentes para predição, análise técnica, roteirização e direção de arte. Cada módulo está preparado para receber um serviço real.",
           selectAll: "SELECIONAR TODOS", clear: "LIMPAR", light: "MODO CLARO", dark: "MODO ESCURO", noData: "SEM DADOS",
           outputLabels: ["B2B · Relatório analítico", "B2C · YouTube Auto-Pilot", "B2C · WhatsApp Auto-Pilot", "B2C · Telegram Auto-Pilot"]
         },
         EN: {
           module: "Select Module", outputs: "Output Formats", advanced: "Advanced Settings", plan: "Active Plan",
           production: "Trigger automated production", automations: "Automations", triggers: "Report triggers", calibration: "Engine calibration",
           terminal: "Market intelligence terminal", description: "Integrated financial intelligence platform with TradFi analysis, crypto module, automations, and specialized agent architecture.",
           deliveries: "Report production bay", deliveriesDescription: "Generate reports and scripts from quotes, benchmarks, and dashboard selections.",
           integrated: "Market map / monitored assets", agents: "Signal orchestration layer", agentsDescription: "Agents for prediction, technical analysis, scripting, and art direction. Each module is ready to receive a real service.",
           selectAll: "SELECT ALL", clear: "CLEAR", light: "LIGHT MODE", dark: "DARK MODE", noData: "NO DATA",
           outputLabels: ["B2B · Analytical report", "B2C · YouTube Auto-Pilot", "B2C · WhatsApp Auto-Pilot", "B2C · Telegram Auto-Pilot"]
         }
       };
       const CATEGORY_NAMES = {
         "Banks & Insurance": "Bancos e Seguradoras", Energy: "Energia", Technology: "Tech", Commodities: "Commodities",
         Retail: "Varejo", "Logistics & Infra": "Logística e Infra.", "Agro & Industry": "Agro e Indústria", "Real Estate": "FIIs e Imobiliário",
         "Layer 1": "Layer 1", "Market Structure": "Estrutura de mercado", Derivatives: "Derivativos", DeFi: "DeFi"
       };
       const t = (value) => configState.language === "EN" ? value : (CATEGORY_NAMES[value] || value);
       const copy = () => LANGUAGE_COPY[configState.language];
       const AGENT_COPY = {
         PT: {
           script: ["Roteirista multi-formato", "Coleta preços, indicadores macro/crypto e sentimento para sintetizar roteiros direcionados para relatório institucional, WhatsApp, Telegram e YouTube.", "EXECUTAR AGENTE"],
           predictive: ["Agente preditivo / machine learning", "Monitora ativos de alta liquidez e registra inferências estatísticas, confidence score e histórico de acurácia para revisão do analista.", "EXECUTAR NOVA INFERÊNCIA"],
           technical: ["Análise técnica avançada", "Processa múltiplos timeframes, identifica formações e organiza níveis operacionais para que a decisão permaneça rastreável.", "EXECUTAR SCANNER DE PADRÕES"],
           art: ["Diretor de arte AI / YouTube Auto-Pilot", "Orquestra roteirização visual, legendas e locução para transformar uma leitura de mercado em conteúdo pronto para revisão humana.", "RENDERIZAR CONTEÚDO"]
         },
         EN: {
           script: ["Multi-format scriptwriter", "Collects prices, macro/crypto indicators, and sentiment to synthesize targeted scripts for institutional reports, WhatsApp, Telegram, and YouTube.", "RUN AGENT"],
           predictive: ["Predictive agent / machine learning", "Monitors high-liquidity assets and records statistical inferences, confidence scores, and accuracy history for analyst review.", "RUN NEW INFERENCE"],
           technical: ["Advanced technical analysis", "Processes multiple timeframes, identifies formations, and organizes operational levels so decisions remain traceable.", "RUN PATTERN SCANNER"],
           art: ["Art director AI / YouTube Auto-Pilot", "Orchestrates visual scripting, captions, and voiceover to turn a market readout into content ready for human review.", "RENDER CONTENT"]
         }
       };
       function persistConfig() {
         localStorage.setItem("omni.categories", JSON.stringify(configState.categories));
         localStorage.setItem("omni.pools", JSON.stringify(configState.pools));
         localStorage.setItem("omni.language", configState.language);
       }
       function applyLanguage() {
         const lang = configState.language;
         const text = copy();
         document.documentElement.lang = lang === "EN" ? "en-US" : "pt-BR";
         $("#language").value = lang;
         $("#module-label").textContent = text.module;
         $("#outputs-label").textContent = text.outputs;
         $("#advanced-label").textContent = text.advanced;
         $("#plan-label").textContent = text.plan;
         $("#production").textContent = text.production;
         $("#terminal-title").textContent = text.terminal;
         $("#page-description").textContent = text.description;
         $("#deliveries-title").textContent = text.deliveries;
         $("#deliveries-description").textContent = text.deliveriesDescription;
         $("#integrated-title").textContent = text.integrated;
         $("#agents-title").textContent = text.agents;
         $("#agents-description").textContent = text.agentsDescription;
         $("#select-all").textContent = text.selectAll;
         $("#clear-all").textContent = text.clear;
         $$(".config-button").forEach((button) => button.textContent = text[button.dataset.config]);
         $$(".check-row").forEach((row, index) => row.lastChild.textContent = ` ${text.outputLabels[index]}`);
         const themeIsLight = document.documentElement.dataset.theme === "light";
         $("#theme-toggle").textContent = themeIsLight ? text.dark : text.light;
         renderAgent(document.querySelector(".tab.active")?.dataset.agent || "script");
       }
       function getAssetPool(module) {
         if (!configState.pools) configState.pools = {};
         if (!configState.pools[module]) {
           configState.pools[module] = categoriesForModule().flatMap(([, assets]) => assets).filter((asset, index, all) => all.findIndex((item) => item[1] === asset[1]) === index);
         }
         return configState.pools[module];
       }
       function renderCalibration() {
         const module = currentModule();
         const categories = categoriesForModule();
         const pool = getAssetPool(module);
         const selectedCategory = $("#manage-category")?.value || categories[0]?.[0] || "";
         const category = categories.find(([name]) => name === selectedCategory);
         const selectedTickers = new Set(category?.[1].map(([, ticker]) => ticker) || []);
         const en = configState.language === "EN";
         $("#modal-title").textContent = en ? "Engine Calibration & Asset/Category Manager" : "Calibragem da engine e gestor de ativos/categorias";
         $("#modal-body").innerHTML = `
           <div class="calibration-grid">
             <div class="field"><label for="calibration-module">${en ? "Module" : "Módulo"}</label><select id="calibration-module"><option value="tradfi" ${module === "tradfi" ? "selected" : ""}>TradFi (Macro)</option><option value="crypto" ${module === "crypto" ? "selected" : ""}>Crypto</option></select></div>
             <div class="field"><label>${en ? "Current asset pool" : "Pool atual de ativos"}</label><select id="calibration-pool" multiple size="6">${pool.map(([name, ticker]) => `<option value="${escapeHtml(ticker)}" selected>${escapeHtml(name)} (${escapeHtml(ticker)})</option>`).join("")}</select><small>${en ? "Deselect assets to remove them from the pool." : "Desmarque ativos para removê-los do pool."}</small></div>
           </div>
           <div class="section-rule"></div>
           <div class="eyebrow" style="color:var(--cyan)">${en ? "Add new asset" : "Adicionar novo ativo"}</div>
           <div class="calibration-grid">
             <div class="field"><label for="new-asset-name">${en ? "Friendly name" : "Nome amigável"}</label><input id="new-asset-name" placeholder="${en ? "Example: Ethereum" : "Ex.: Ethereum"}" /></div>
             <div class="field"><label for="new-asset-ticker">${en ? "Ticker" : "Ticker"}</label><input id="new-asset-ticker" placeholder="${en ? "Example: ETH-USD" : "Ex.: ETH-USD"}" /></div>
           </div>
           <div class="section-rule"></div>
           <div class="eyebrow" style="color:var(--cyan)">${en ? "Manage categories" : "Gerenciar categorias"}</div>
           <div class="field"><label for="manage-category">${en ? "Category to manage" : "Categoria para gerenciar"}</label><select id="manage-category">${categories.map(([name]) => `<option value="${escapeHtml(name)}" ${name === selectedCategory ? "selected" : ""}>${escapeHtml(t(name))}</option>`).join("")}</select></div>
           <div class="calibration-grid">
             <div class="field"><label for="rename-category">${en ? "Rename category" : "Renomear categoria"}</label><input id="rename-category" value="${escapeHtml(selectedCategory)}" /></div>
             <div class="field"><label for="category-assets">${en ? "Assets in category" : "Ativos na categoria"}</label><select id="category-assets" multiple size="6">${pool.map(([name, ticker]) => `<option value="${escapeHtml(ticker)}" ${selectedTickers.has(ticker) ? "selected" : ""}>${escapeHtml(name)} (${escapeHtml(ticker)})</option>`).join("")}</select></div>
           </div>
           <label class="check-row"><input id="delete-category" type="checkbox" /> ${en ? "Delete this category" : "Excluir esta categoria"}</label>
           <div class="section-rule"></div>
           <div class="eyebrow" style="color:var(--cyan)">${en ? "Create new category" : "Criar nova categoria"}</div>
           <div class="calibration-grid">
             <div class="field"><label for="new-category-name">${en ? "Category name" : "Nome da categoria"}</label><input id="new-category-name" placeholder="${en ? "Example: 9 - DeFi & Web3" : "Ex.: 9 - DeFi & Web3"}" /></div>
             <div class="field"><label for="new-category-assets">${en ? "Assets for new category" : "Ativos da nova categoria"}</label><select id="new-category-assets" multiple size="6">${pool.map(([name, ticker]) => `<option value="${escapeHtml(ticker)}">${escapeHtml(name)} (${escapeHtml(ticker)})</option>`).join("")}</select></div>
           </div>
           <button class="button" id="calibration-save">${en ? "SAVE PARAMETERS" : "SALVAR PARÂMETROS"}</button>
           <div id="calibration-feedback" class="data-meta"></div>`;
         $("#calibration-module").addEventListener("change", () => {
           document.querySelector(`input[name="module"][value="${$("#calibration-module").value}"]`).checked = true;
           renderCalibration();
         });
         $("#manage-category").addEventListener("change", renderCalibration);
         $("#calibration-save").addEventListener("click", saveCalibration);
       }
       function saveCalibration() {
         const module = $("#calibration-module").value;
         const categories = configState.categories[module];
         const selectedCategory = $("#manage-category").value;
         const poolByTicker = new Map(getAssetPool(module).map((asset) => [asset[1], asset]));
         const selectedPool = Array.from($("#calibration-pool").selectedOptions).map((option) => poolByTicker.get(option.value)).filter(Boolean);
         const newName = $("#new-asset-name").value.trim();
         const newTicker = $("#new-asset-ticker").value.trim().toUpperCase();
         if (newName && newTicker && !poolByTicker.has(newTicker)) selectedPool.push([newName, newTicker]);
         configState.pools[module] = selectedPool;
         const categoryIndex = categories.findIndex(([name]) => name === selectedCategory);
         if (categoryIndex >= 0) {
           if ($("#delete-category").checked) categories.splice(categoryIndex, 1);
           else {
             const renamed = $("#rename-category").value.trim() || selectedCategory;
             const selectedAssets = new Set(Array.from($("#category-assets").selectedOptions).map((option) => option.value));
             categories[categoryIndex] = [renamed, selectedPool.filter(([, ticker]) => selectedAssets.has(ticker))];
           }
         }
         const newCategoryName = $("#new-category-name").value.trim();
         if (newCategoryName && !categories.some(([name]) => name === newCategoryName)) {
           const newAssets = new Set(Array.from($("#new-category-assets").selectedOptions).map((option) => option.value));
           categories.push([newCategoryName, selectedPool.filter(([, ticker]) => newAssets.has(ticker))]);
         }
         persistConfig();
         renderModule();
         $("#calibration-feedback").textContent = configState.language === "EN" ? "Parameters saved locally for this dashboard." : "Parâmetros salvos localmente para este dashboard.";
         toast(configState.language === "EN" ? "Engine calibration saved." : "Calibragem da engine salva.");
       }
      const toast = (message) => {
        const element = $("#toast");
        element.textContent = message;
        element.classList.add("show");
        clearTimeout(window.__toastTimer);
        window.__toastTimer = setTimeout(() => element.classList.remove("show"), 3200);
      };
      const currentModule = () => document.querySelector('input[name="module"]:checked').value;
      const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[character]);
      const formatNumber = (value, currency = "USD") => new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
      const formatPercent = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}%`;
      const formatTime = (value) => value ? new Date(value).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "medium" }) : "timestamp unavailable";
      const statusMarkup = (quote, overview = marketState.data) => {
        const stale = quote ? quote.isStale : overview?.isStale;
        const status = quote?.dataStatus || overview?.dataStatus || "demo";
        const source = quote?.source || overview?.source || "unknown provider";
        const timestamp = quote?.timestamp || overview?.asOf;
        return `<div class="data-meta ${stale ? "stale" : ""}"><span class="data-status ${status}">${status.toUpperCase()}${stale ? " · STALE" : ""}</span>· ${escapeHtml(source)} · ${escapeHtml(formatTime(timestamp))}</div>${quote?.error ? `<div class="stale-note">Provider warning: ${escapeHtml(quote.error)}</div>` : ""}`;
      };
      const quoteFor = (symbol) => marketState.data?.assets?.find((asset) => asset.symbol === symbol);
      const displayPrice = (quote) => quote ? `${quote.assetClass === "equity" && quote.symbol.endsWith(".SA") ? "R$ " : "$ "}${formatNumber(quote.price)}` : "NO DATA";
      const trendClass = (value) => value > 0 ? "positive" : value < 0 ? "negative" : "neutral";

      function renderCategories() {
         const categories = categoriesForModule();
        const assets = marketState.data?.assets || [];
        $("#category-grid").innerHTML = categories.map(([name, categoryAssets]) => `
          <div class="category-card">
             <div class="category-top"><div class="category-name" title="${escapeHtml(t(name))}">${escapeHtml(t(name))}</div><input type="checkbox" data-category="${escapeHtml(name)}" checked onchange="renderReport()" aria-label="${configState.language === "EN" ? "Include" : "Incluir"} ${escapeHtml(t(name))}" /></div>
            ${categoryAssets.map(([asset, ticker]) => {
              const quote = assets.find((item) => item.symbol === ticker);
               return `<div class="asset-row"><div class="asset-name">${escapeHtml(asset)}<br /><span class="mono" style="font-size:8px;color:var(--muted-2)">${escapeHtml(ticker)}</span></div><div class="asset-detail ${trendClass(quote?.changePercent || 0)}">${quote ? `${displayPrice(quote)} ${formatPercent(quote.changePercent)}` : copy().noData}</div>${statusMarkup(quote)}</div>`;
            }).join("")}
          </div>
        `).join("");
      }

      function renderMetrics() {
        const overview = marketState.data;
        if (!overview) { $("#metric-list").innerHTML = `<div class="${marketState.error ? "api-error" : "loading-state"}">${escapeHtml(marketState.error || "Connecting to the market data service…")}</div>`; return; }
        const metrics = overview.metrics || [];
        $("#metric-list").innerHTML = metrics.map((metric) => `<div class="metric-card"><div class="metric-top"><span>${escapeHtml(metric.label)}</span><span class="source">${escapeHtml(metric.source)}</span></div><div class="metric-value">${escapeHtml(metric.value)}</div><div class="${trendClass(metric.changeValue || 0)}">${escapeHtml(metric.change)}</div>${statusMarkup(null, overview)}</div>`).join("");
      }

      function renderReport() {
        const overview = marketState.data;
        if (!overview) { $("#report").value = ""; return; }
        const moduleName = currentModule() === "crypto" ? "CRYPTO" : "TRADFI (MACRO)";
        const selected = new Set(Array.from(document.querySelectorAll("#category-grid input[data-category]:checked")).map((input) => input.dataset.category));
        const categories = categoriesForModule();
        const lines = [`=== OMNI ${moduleName} REPORT ===`, configState.language === "EN" ? "Issuer: OMNIRESEARCH Engine | Analyst ID: CNPI-T 0000" : "Emissor: OMNIRESEARCH Engine | ID do analista: CNPI-T 0000", `Timestamp: ${formatTime(overview.asOf)} | Language: ${configState.language}`, `${configState.language === "EN" ? "Market state" : "Estado do mercado"}: ${overview.dataStatus}${overview.isStale ? " / STALE DATA" : ""}`, "", "--- ASSETS & MONITORED CATEGORIES ---"];
        categories.forEach(([categoryName, categoryAssets]) => {
          if (selected.size && !selected.has(categoryName)) return;
          lines.push("", `[${categoryName.toUpperCase()}]`);
          categoryAssets.forEach(([assetName, ticker]) => {
            const quote = overview.assets.find((item) => item.symbol === ticker);
            if (quote) lines.push(`${quote.name} (${quote.symbol}): ${displayPrice(quote)} (${formatPercent(quote.changePercent)}) | ${quote.source} | ${quote.dataStatus}${quote.isStale ? " / STALE" : ""} | ${formatTime(quote.timestamp)}`);
          });
        });
        lines.push("", `Sources: ${overview.source}`, `Status: ${overview.dataStatus}${overview.isStale ? " / provider warnings present" : " / provider responses nominal"}`);
        if (overview.errors?.length) lines.push("", "Provider warnings:", ...overview.errors);
        $("#report").value = lines.join("\n");
      }

      function renderHeatmap() {
        const overview = marketState.data;
        const heat = overview?.heatmap;
        if (!heat || !heat.prices?.length) { $("#heatmap-visual").innerHTML = `<div class="loading-state">No liquidity series available.</div>`; $("#heatmap-note").innerHTML = `<div class="loading-state">${escapeHtml(heat?.source || "Provider series unavailable")}</div>`; return; }
        const max = Math.max(...heat.volumes, 1);
        $("#heatmap-visual").innerHTML = `<div class="eyebrow" style="color:var(--amber)">${escapeHtml(heat.title)}</div>${heat.prices.map((price, i) => { const width = Math.round(18 + (heat.volumes[i] / max) * 78); return `<div class="bar-row"><span>${escapeHtml(formatNumber(price))}</span><div class="bar-track"><div class="bar" style="width:${width}%"></div></div><span>${escapeHtml(Number(heat.volumes[i]).toFixed(2))}${escapeHtml(heat.unit)}</span></div>`; }).join("")}<div class="section-rule"></div><div class="mono" style="font-size:10px;color:var(--cyan)">SPOT · ${escapeHtml(displayPrice({price: heat.basePrice, assetClass: heat.module === "crypto" ? "crypto" : "equity", symbol: heat.module === "crypto" ? "BTC-USD" : "ES=F"}))}</div><div class="data-meta">${escapeHtml(heat.source)} · ${escapeHtml(formatTime(heat.timestamp))}</div>`;
        $("#heatmap-note").innerHTML = `<div class="eyebrow" style="color:var(--purple);margin-bottom:10px">Analyst readout</div><p><strong>${escapeHtml(heat.note)}</strong></p><div class="agent-kpis" style="margin-top:22px"><div class="mini-kpi"><div class="eyebrow">Spot</div><strong>${escapeHtml(formatNumber(heat.basePrice))}</strong></div><div class="mini-kpi"><div class="eyebrow">Source</div><strong>${escapeHtml(heat.source)}</strong></div><div class="mini-kpi"><div class="eyebrow">Clusters</div><strong>${heat.prices.length}</strong></div></div>`;
      }

      function renderModule() {
        const crypto = currentModule() === "crypto";
        $("#metrics-title").textContent = crypto ? "Crypto Market" : "TradFi (Macro)";
        $("#report-module").textContent = crypto ? "CRYPTO" : "TRADFI (MACRO)";
        $("#heatmap-title").textContent = crypto ? "Provider price path / Bitcoin" : "Provider price path / S&P 500";
        const overview = marketState.data;
        $("#source-label").textContent = overview?.source || "CONNECTING";
        $("#date-label").textContent = overview?.asOf ? new Date(overview.asOf).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).toUpperCase() : "--";
        $("#auto-status").classList.toggle("live", !overview?.isStale);
        $("#auto-status").innerHTML = `<span class="status-dot${overview?.isStale ? " stale" : ""}"></span><strong>${overview?.dataStatus?.toUpperCase() || "CONNECTING"}</strong> · ${overview?.isStale ? "stale data visible" : "provider monitoring"}`;
        $("#api-status").innerHTML = `<i class="status-dot${overview?.isStale ? " stale" : ""}"></i>API STATUS · ${overview ? (overview.isStale ? "STALE WARNINGS" : "NOMINAL") : "CONNECTING"}`;
        $("#health").textContent = overview?.isStale ? "● DATA HEALTH · STALE" : overview ? "● DATA HEALTH · NOMINAL" : "● DATA HEALTH · CONNECTING";
        renderCategories();
        renderMetrics();
        renderReport();
        renderHeatmap();
      }

      async function loadMarketData(announce = false) {
        const boot = window.__OMNI_BOOTSTRAP__?.[currentModule()];
        if (boot) { marketState.data = boot; marketState.error = null; marketState.loading = false; renderModule(); if (announce) toast("Market data refreshed."); return; }
        const request = ++marketState.request;
        marketState.loading = true;
        marketState.error = null;
        if (!marketState.data) renderModule();
        try {
          const response = await fetch(`/api/market/overview?module=${encodeURIComponent(currentModule())}`, { cache: "no-store" });
          if (!response.ok) throw new Error(`Market API returned HTTP ${response.status}`);
          const data = await response.json();
          if (request !== marketState.request) return;
          marketState.data = data;
          marketState.loading = false;
          renderModule();
          if (announce) toast(data.isStale ? "Provider warning: stale or demo values are marked in the dashboard." : "Live market data refreshed.");
        } catch (error) {
          if (request !== marketState.request) return;
          marketState.loading = false;
          marketState.error = error instanceof Error ? error.message : "Unable to load market data";
          renderModule();
          toast(`Market data unavailable: ${marketState.error}`);
        }
      }

      function updateClock() {
        const now = new Date();
        $("#clock").textContent = now.toLocaleTimeString("pt-BR", { hour12: false }) + " BRT";
      }

      $$('input[name="module"]').forEach((input) => input.addEventListener("change", () => {
        marketState.data = null;
        renderModule();
        loadMarketData(true);
        toast(currentModule() === "crypto" ? "Loading Crypto provider data…" : "Loading TradFi provider data…");
      }));

       function renderAgent(agent) {
         const content = $("#agent-content");
         const [title, description, action] = AGENT_COPY[configState.language][agent];
         content.querySelector("h3").textContent = title;
         content.querySelector("p").textContent = description;
         content.querySelector("#run-agent").textContent = action;
         const controls = content.querySelectorAll("label");
         controls[0].textContent = configState.language === "EN" ? "Target asset for script" : "Ativo alvo para roteiro";
         controls[1].textContent = configState.language === "EN" ? "Script tone" : "Tom do roteiro";
       }
       $$(".tab").forEach((tab) => tab.addEventListener("click", () => {
         $$(".tab").forEach((item) => item.classList.remove("active"));
         tab.classList.add("active");
         renderAgent(tab.dataset.agent);
         toast(`${AGENT_COPY[configState.language][tab.dataset.agent][0]} selected.`);
       }));

      $("#refresh").addEventListener("click", () => loadMarketData(true));
      $("#print").addEventListener("click", () => window.print());
      $("#health").addEventListener("click", () => toast(marketState.data?.isStale ? "Provider warnings are visible on affected values." : "All selected providers responded nominally."));
      $("#production").addEventListener("click", () => toast("Production queue armed. Select an output format to dispatch."));
      $("#crm-push").addEventListener("click", () => toast("CRM payload prepared in preview mode. No external request was sent."));
      $("#run-agent").addEventListener("click", () => toast("Agent execution queued for analyst review."));
      $("#heatmap-report").addEventListener("click", (event) => {
        event.currentTarget.classList.toggle("green");
        toast(event.currentTarget.classList.contains("green") ? "Liquidity module included in report." : "Liquidity module removed from report.");
      });
      $("#select-all").addEventListener("click", () => { $$("#category-grid input").forEach((input) => input.checked = true); renderReport(); });
      $("#clear-all").addEventListener("click", () => { $$("#category-grid input").forEach((input) => input.checked = false); renderReport(); });
      $$("[data-export]").forEach((button) => button.addEventListener("click", () => {
        const type = button.dataset.export;
        const content = $("#report").value;
        if (type === "PDF") window.print();
        else {
          const payload = type === "JSON" ? JSON.stringify({ module: currentModule(), generatedAt: new Date().toISOString(), content }, null, 2) : content;
          const blob = new Blob([payload], { type: type === "JSON" ? "application/json" : "text/plain" });
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = `OMNI_Report_${currentModule()}.${type.toLowerCase()}`;
          link.click();
          URL.revokeObjectURL(link.href);
          toast(`${type} export generated.`);
        }
      }));
       $("#theme-toggle").addEventListener("click", () => {
        const light = document.documentElement.dataset.theme === "light";
        document.documentElement.dataset.theme = light ? "dark" : "light";
         $("#theme-toggle").textContent = light ? copy().light : copy().dark;
      });
       $("#language").addEventListener("change", (event) => {
         configState.language = event.target.value;
         persistConfig();
         applyLanguage();
         renderModule();
       });
       $$(".config-button").forEach((button) => button.addEventListener("click", () => {
         const en = configState.language === "EN";
         const key = button.dataset.config;
         if (key === "calibration") renderCalibration();
         else {
           $("#modal-title").textContent = key === "automations"
             ? (en ? "Automation settings & CRM integrators" : "Automações e integrações CRM")
             : (en ? "Automated report triggers" : "Gatilhos automáticos de report");
           $("#modal-body").innerHTML = `<div class="field"><label>${en ? "Dispatch channels" : "Canais de distribuição"}</label><input placeholder="${en ? "Email, webhook, CRM" : "E-mail, webhook, CRM"}" /></div><div class="field"><label>${en ? "Schedule" : "Agendamento"}</label><select><option>${en ? "After market close" : "Após fechamento do mercado"}</option><option>${en ? "Every refresh" : "A cada atualização"}</option></select></div><button class="button" id="config-save">${en ? "SAVE CONFIGURATION" : "SALVAR CONFIGURAÇÃO"}</button>`;
           $("#config-save").addEventListener("click", () => toast(en ? "Configuration saved locally." : "Configuração salva localmente."));
         }
         $("#modal").classList.add("open");
       }));
      $("#modal-close").addEventListener("click", () => $("#modal").classList.remove("open"));
      $("#modal").addEventListener("click", (event) => { if (event.target.id === "modal") $("#modal").classList.remove("open"); });
      document.addEventListener("keydown", (event) => { if (event.key === "Escape") $("#modal").classList.remove("open"); });

       applyLanguage();
       renderModule();
      loadMarketData();
      updateClock();
      setInterval(updateClock, 1000);
    </script>
  </body>
</html>"""
html = html.replace("__OMNI_BOOTSTRAP_PLACEHOLDER__", json.dumps(bootstrap, ensure_ascii=False))
components.html(html, height=3400, scrolling=True)
