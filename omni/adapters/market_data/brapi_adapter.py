import logging
from typing import Dict, List

import requests

from omni.domain.models import Quote

logger = logging.getLogger(__name__)


class BrapiMarketDataAdapter:
    def fetch_quotes(self, failed_symbols: List[str], token: str = "") -> Dict[str, Quote]:
        brapi_quotes: Dict[str, Quote] = {}
        if not failed_symbols:
            return brapi_quotes

        token_clean = token.split("=")[-1].strip().replace('"', "").replace("'", "") if token else ""
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
                        brapi_quotes[orig_sym] = Quote(float(price), float(chg))
        except Exception:
            logger.warning("BRAPI fallback request failed", exc_info=True)

        return brapi_quotes
