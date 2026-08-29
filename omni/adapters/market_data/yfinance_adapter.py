import logging
from typing import Dict, Tuple

import yfinance as yf

from omni.domain.models import Quote

logger = logging.getLogger(__name__)

ALIAS_MAP = {"UNI-USD": "UNI7083-USD"}


class YFinanceMarketDataAdapter:
    def fetch_quotes(self, symbols: Tuple[str, ...]) -> Dict[str, Quote]:
        quotes = {sym: Quote() for sym in symbols}
        try:
            download_list = [ALIAS_MAP.get(s, s) for s in symbols]
            if "ES=F" not in download_list:
                download_list.append("ES=F")
            df_data = yf.download(download_list, period="5d", interval="1d", group_by="ticker", progress=False)
            for orig_sym in symbols + ("ES=F",):
                actual_sym = ALIAS_MAP.get(orig_sym, orig_sym)
                try:
                    df_sym = df_data if len(download_list) == 1 else (
                        df_data[actual_sym] if actual_sym in df_data.columns.get_level_values(0) else None
                    )
                    if df_sym is not None and not df_sym.empty:
                        df_clean = df_sym.dropna(subset=["Close"])
                        if len(df_clean) >= 1:
                            p = float(df_clean["Close"].iloc[-1])
                            prev = float(df_clean["Close"].iloc[-2]) if len(df_clean) >= 2 else p
                            c = ((p - prev) / prev) * 100 if prev > 0 else 0.0
                            if p > 0:
                                quotes[orig_sym] = Quote(p, c)
                except Exception:
                    logger.debug("yfinance batch parse failed for %s", orig_sym, exc_info=True)
        except Exception:
            logger.warning("yfinance batch download failed", exc_info=True)

        for orig_sym in [s for s, v in quotes.items() if v.price == 0.0]:
            try:
                hist = yf.Ticker(ALIAS_MAP.get(orig_sym, orig_sym)).history(period="5d").dropna(subset=["Close"])
                if not hist.empty:
                    p = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else p
                    c = ((p - prev) / prev) * 100 if prev > 0 else 0.0
                    if p > 0:
                        quotes[orig_sym] = Quote(p, c)
            except Exception:
                logger.debug("yfinance per-ticker fallback failed for %s", orig_sym, exc_info=True)

        return quotes

    def fetch_price_history(self, ticker: str, period: str = "3mo", interval: str = "1h"):
        try:
            return yf.download(ticker, period=period, interval=interval, progress=False)
        except Exception:
            logger.warning("yfinance history download failed for %s", ticker, exc_info=True)
            return None
