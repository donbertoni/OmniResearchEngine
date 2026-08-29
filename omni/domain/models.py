from dataclasses import dataclass
from typing import List


@dataclass
class Quote:
    price: float = 0.0
    change: float = 0.0


@dataclass
class MarketSentiment:
    value: str
    classification: str


@dataclass
class GlobalCryptoStats:
    btc_dominance_display: str
    btc_dominance_change: float
    usdt_dominance_display: str
    usdt_dominance_change: float


@dataclass
class LiquidityData:
    prices: List[float]
    volumes: List[float]
    source_label: str
    unit_label: str


@dataclass(frozen=True)
class TierPermissions:
    allow_customization: bool
    allow_white_label: bool
    max_free_tickers: int
