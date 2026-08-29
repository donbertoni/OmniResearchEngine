"""Portas (interfaces) que a camada de aplicação usa para falar com o mundo externo.

Nenhum destes Protocols importa Streamlit ou bibliotecas de rede — só os adapters
(em omni/adapters) implementam essas portas de fato.
"""

from typing import Dict, Protocol, Tuple

from omni.domain.models import GlobalCryptoStats, LiquidityData, MarketSentiment, Quote


class MarketDataPort(Protocol):
    def fetch_quotes(self, symbols: Tuple[str, ...], brapi_token: str = "", custom_api_key: str = "") -> Dict[str, Quote]: ...


class SentimentPort(Protocol):
    def fetch_fear_greed(self) -> MarketSentiment: ...


class GlobalMarketPort(Protocol):
    def fetch_global_stats(self) -> GlobalCryptoStats: ...


class LiquidityDataPort(Protocol):
    def fetch_liquidity_data(self, base_price: float) -> LiquidityData: ...


class ReportExporterPort(Protocol):
    def to_pdf(self, text_content: str, company: str, timestamp: str) -> bytes: ...


class NotificationPort(Protocol):
    def send(self, target: str, message: str, credentials: dict) -> Tuple[bool, str]: ...


class TriggerConfigRepositoryPort(Protocol):
    def save(self, config_data: dict) -> Tuple[bool, str]: ...

    def load(self) -> dict: ...
