from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from omni.domain.models import GlobalCryptoStats, MarketSentiment, Quote
from omni.domain.ports import GlobalMarketPort, MarketDataPort, SentimentPort


@dataclass
class DashboardSnapshot:
    quotes: Dict[str, Quote]
    sentiment: MarketSentiment
    global_stats: GlobalCryptoStats
    warnings: List[str] = field(default_factory=list)


def fetch_dashboard_snapshot(
    market_data_port: MarketDataPort,
    sentiment_port: SentimentPort,
    global_market_port: GlobalMarketPort,
    symbols: Tuple[str, ...],
    brapi_token: str = "",
) -> DashboardSnapshot:
    # As três chamadas vão para provedores diferentes e nenhuma depende do
    # resultado da outra -- rodar em paralelo faz o tempo de espera ser o
    # máximo das três, não a soma, em cada cache-miss de 60s.
    with ThreadPoolExecutor(max_workers=3) as executor:
        quotes_future = executor.submit(market_data_port.fetch_quotes, symbols, brapi_token=brapi_token)
        sentiment_future = executor.submit(sentiment_port.fetch_fear_greed)
        global_stats_future = executor.submit(global_market_port.fetch_global_stats)

        quotes = quotes_future.result()
        sentiment = sentiment_future.result()
        global_stats = global_stats_future.result()

    # Falha de adapter era invisível: um símbolo sem cotação real virava
    # silenciosamente Quote(0.0, 0.0) e a UI só mostrava "0"/"--", sem indicar
    # se aquilo era um preço real ou um fallback. Agora isso vira um aviso
    # explícito exibido no topo do dashboard.
    warnings = [
        f"Sem cotação real para {symbol} (fonte indisponível) -- exibindo 0 como fallback."
        for symbol in symbols
        if quotes.get(symbol, Quote()).price == 0.0
    ]

    return DashboardSnapshot(quotes=quotes, sentiment=sentiment, global_stats=global_stats, warnings=warnings)
