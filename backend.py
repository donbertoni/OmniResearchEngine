import io
import json
import requests
import pandas as pd
import yfinance as yf

# -----------------------------------------------------------------------------
# ACERVO MESTRE DE DADOS & CATEGORIAS (TRADFI & CRYPTO)
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
# FUNÇÕES AUXILIARES E DE INGESTÃO
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

def fetch_btc_fng():
    try:
        res = requests.get("https://api.alternative.me/fng/", timeout=3)
        if res.status_code == 200:
            data = res.json()["data"][0]
            return data.get("value", "62") + " / 100", data.get("value_classification", "Greed")
    except Exception:
        pass
    return "62 / 100", "Greed"

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
                    brapi_quotes[orig_sym] = {"price": float(price), "change": float(chg), "source": "BRAPI"}
    except Exception:
        pass
    return brapi_quotes

def fetch_realtime_quotes(symbols_tuple, brapi_token=""):
    quotes = {sym: {"price": 0.0, "change": 0.0, "source": "Unavailable"} for sym in symbols_tuple}
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
                            quotes[orig_sym] = {"price": p, "change": c, "source": "Yahoo Finance"}
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
                    quotes[orig_sym] = {"price": p, "change": c, "source": "Yahoo Finance"}
        except Exception:
            pass

    failed_b3 = [sym for sym, val in quotes.items() if (val["price"] == 0.0 or pd.isna(val["price"])) and sym.endswith(".SA")]
    if failed_b3:
        for sym, data_dict in fetch_brapi_fallback(failed_b3, token=brapi_token).items():
            quotes[sym] = data_dict
    return quotes


# -----------------------------------------------------------------------------
# OMNI RESEARCH ENGINE - API FLASK
# -----------------------------------------------------------------------------
import os
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response, send_from_directory

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
if CORS:
    CORS(app, resources={r"/api/*": {"origins": os.getenv("OMNI_CORS_ORIGINS", "*").split(",")}})

BRAPI_TOKEN = os.getenv("BRAPI_TOKEN", "")
CACHE_TTL = int(os.getenv("OMNI_CACHE_TTL", "60"))
_market_cache = {}


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _module_name(value):
    return "crypto" if str(value or "tradfi").lower() == "crypto" else "tradfi"


def _module_catalog(module):
    source = CATEGORIES_CRYPTO if module == "crypto" else {
        key: value for key, value in CATEGORIES_TRADFI.items()
        if "Crypto" not in key and "Digital" not in value.get("tag", "")
    }
    categories = []
    symbols = []
    for category, data in source.items():
        assets = []
        for item in data.get("assets", []):
            name, symbol = item[0], item[1]
            assets.append((name, symbol))
            if symbol not in symbols:
                symbols.append(symbol)
        categories.append((category, assets))
    return categories, symbols


def _quote_payload(name, symbol, quote, timestamp, source, status, error=None, sparkline=None):
    price = float(quote.get("price", 0) or 0)
    change = float(quote.get("change", 0) or 0)
    return {
        "name": name, "symbol": symbol, "price": price,
        "changePercent": change,
        "assetClass": "crypto" if ("-USD" in symbol or symbol in {"BTC-USD", "ETH-USD"}) else "equity",
        "source": source, "dataStatus": status, "isStale": status != "live",
        "timestamp": timestamp, "sparkline": sparkline or [], "error": error,
    }


def _load_overview(module, force=False):
    module = _module_name(module)
    now = time.time()
    cached = _market_cache.get(module)
    if cached and not force and now - cached["created"] < CACHE_TTL:
        return cached["data"]
    categories, symbols = _module_catalog(module)
    if module == "tradfi":
        symbols = symbols + [item["ticker"] for item in MACRO_BENCHMARKS]
    else:
        symbols = symbols + [item["ticker"] for item in CRYPTO_BENCHMARKS if item.get("ticker")]
    symbols = tuple(dict.fromkeys(symbols))
    timestamp = _utc_now()
    errors = []
    try:
        raw_quotes = fetch_realtime_quotes(symbols, brapi_token=BRAPI_TOKEN)
    except Exception as exc:
        raw_quotes = {symbol: {"price": 0.0, "change": 0.0} for symbol in symbols}
        errors.append(f"Quote provider error: {exc}")
    assets = []
    for category, category_assets in categories:
        for name, symbol in category_assets:
            quote = raw_quotes.get(symbol, {"price": 0.0, "change": 0.0})
            status = "live" if quote.get("price", 0) else "unavailable"
            assets.append(_quote_payload(name, symbol, quote, timestamp, "Yahoo Finance / BRAPI", status))
    benchmarks = []
    benchmark_defs = MACRO_BENCHMARKS if module == "tradfi" else CRYPTO_BENCHMARKS
    for definition in benchmark_defs:
        symbol = definition.get("ticker")
        if not symbol:
            continue
        quote = raw_quotes.get(symbol, {"price": 0.0, "change": 0.0})
        benchmarks.append(_quote_payload(definition["label"], symbol, quote, timestamp, definition.get("badge", "provider"), "live" if quote.get("price") else "unavailable"))
    all_quotes = assets + benchmarks
    available = [item for item in all_quotes if item["price"] > 0]
    overview = {
        "module": module, "asOf": timestamp,
        "source": "Yahoo Finance / BRAPI fallback",
        "dataStatus": "live" if available else "unavailable",
        "isStale": not bool(available), "assets": all_quotes,
        "categories": [{"name": name, "assets": [{"name": n, "symbol": s} for n, s in items]} for name, items in categories],
        "benchmarks": benchmarks,
        "kpis": {"advancing": sum(1 for x in available if x["changePercent"] > 0), "declining": sum(1 for x in available if x["changePercent"] < 0), "total": len(all_quotes), "available": len(available)},
        "errors": errors + (["No provider quote returned for the selected symbols."] if not available else []),
    }
    _market_cache[module] = {"created": now, "data": overview}
    return overview


def _report_text(module, selected_symbols=None):
    overview = _load_overview(module)
    selected = set(selected_symbols or [])
    assets = [x for x in overview["assets"] if not selected or x["symbol"] in selected]
    lines = [f"=== OMNI {module.upper()} REPORT ===", "Emissor: OMNIRESEARCH Engine | Modo: pesquisa e educação financeira", f"Gerado em: {overview['asOf']}", f"Status dos dados: {overview['dataStatus']}", "", "--- COTAÇÕES NORMALIZADAS ---"]
    for item in assets:
        price = fmt_num(item["price"]) if item["price"] else "--"
        lines.append(f"{item['name']} ({item['symbol']}): {price} | {fmt_pct(item['changePercent'])} | {item['source']} | {item['dataStatus']}")
    lines += ["", f"Fontes: {overview['source']}", f"Amplitude: {overview['kpis']['advancing']} altas / {overview['kpis']['declining']} baixas"]
    if overview.get("errors"):
        lines += ["", "Avisos:"] + [f"- {error}" for error in overview["errors"]]
    return "\n".join(lines)


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "omni-research-engine", "timestamp": _utc_now()})


@app.get("/api/market/overview")
def market_overview():
    return jsonify(_load_overview(request.args.get("module"), request.args.get("refresh") == "1"))


@app.post("/api/market/refresh")
def market_refresh():
    payload = request.get_json(silent=True) or {}
    return jsonify(_load_overview(payload.get("module"), force=True))


@app.post("/api/report")
def create_report():
    payload = request.get_json(silent=True) or {}
    module = _module_name(payload.get("module"))
    return jsonify({"ok": True, "module": module, "generatedAt": _utc_now(), "content": _report_text(module, payload.get("symbols"))})


@app.post("/api/report/pdf")
def report_pdf():
    payload = request.get_json(silent=True) or {}
    module = _module_name(payload.get("module"))
    return Response(generate_pdf_report(_report_text(module, payload.get("symbols")), f"OMNI {module.upper()} REPORT", _utc_now()), mimetype="application/pdf", headers={"Content-Disposition": f"attachment; filename=OMNI_Report_{module}.pdf"})


@app.post("/api/agents/run")
def run_agent():
    payload = request.get_json(silent=True) or {}
    module = _module_name(payload.get("module"))
    asset, agent, tone = payload.get("asset", ""), payload.get("agent", "script"), payload.get("tone", "Institucional / B2B")
    return jsonify({"ok": True, "status": "queued_for_review", "agent": agent, "module": module, "asset": asset, "tone": tone, "output": _report_text(module, [asset] if asset else None), "generatedAt": _utc_now()})


@app.post("/api/crm/push")
def crm_push():
    payload = request.get_json(silent=True) or {}
    webhook = os.getenv("OMNI_CRM_WEBHOOK", "").strip()
    result = {"ok": True, "status": "preview", "message": "CRM payload prepared; no external request was sent.", "payload": payload}
    if webhook and payload.get("dispatch") is True:
        try:
            response = requests.post(webhook, json=payload, timeout=8)
            result.update({"status": "sent" if response.ok else "error", "httpStatus": response.status_code})
        except Exception as exc:
            result.update({"status": "error", "message": str(exc)})
    return jsonify(result)


@app.errorhandler(Exception)
def handle_error(error):
    app.logger.exception("Unhandled API error")
    return jsonify({"ok": False, "error": str(error)}), 500


@app.get("/")
def dashboard():
    return send_from_directory("/home/ubuntu", "Omnidashboard.html")


if __name__ == "__main__":
    app.run(host=os.getenv("OMNI_HOST", "0.0.0.0"), port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "0") == "1")
