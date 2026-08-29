from typing import Dict, Tuple

from omni.domain.models import Quote


class CompositeMarketDataAdapter:
    """Implementa MarketDataPort: cotações via yfinance, com fallback BRAPI para
    tickers .SA (B3) que o yfinance não conseguiu resolver."""

    def __init__(self, yfinance_adapter, brapi_adapter):
        self._yfinance = yfinance_adapter
        self._brapi = brapi_adapter

    def fetch_quotes(self, symbols: Tuple[str, ...], brapi_token: str = "", custom_api_key: str = "") -> Dict[str, Quote]:
        quotes = self._yfinance.fetch_quotes(symbols)
        failed_b3 = [sym for sym, q in quotes.items() if q.price == 0.0 and sym.endswith(".SA")]
        if failed_b3:
            fallback = self._brapi.fetch_quotes(failed_b3, token=brapi_token)
            quotes.update(fallback)
        return quotes
