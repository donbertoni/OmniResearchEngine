from dataclasses import dataclass
from typing import Dict, Tuple

from omni.domain.models import GlobalCryptoStats, MarketSentiment, Quote
from omni.domain.ports import GlobalMarketPort, MarketDataPort, SentimentPort


@dataclass
class DashboardSnapshot:
    quotes: Dict[str, Quote]
    sentiment: MarketSentiment
    global_stats: GlobalCryptoStats


def fetch_dashboard_snapshot(
    market_data_port: MarketDataPort,
    sentiment_port: SentimentPort,
    global_market_port: GlobalMarketPort,
    symbols: Tuple[str, ...],
    brapi_token: str = "",
    custom_api_key: str = "",
) -> DashboardSnapshot:
    quotes = market_data_port.fetch_quotes(symbols, brapi_token=brapi_token, custom_api_key=custom_api_key)
    sentiment = sentiment_port.fetch_fear_greed()
    global_stats = global_market_port.fetch_global_stats()
    return DashboardSnapshot(quotes=quotes, sentiment=sentiment, global_stats=global_stats)
