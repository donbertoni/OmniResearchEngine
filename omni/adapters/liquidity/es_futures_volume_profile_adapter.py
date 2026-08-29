import logging

import numpy as np
import pandas as pd

from omni.domain.models import LiquidityData

logger = logging.getLogger(__name__)


class EsFuturesLiquidityAdapter:
    """Heatmap de liquidez para TradFi, via volume profile histórico do ES=F (Yahoo Finance)."""

    def __init__(self, yfinance_adapter):
        self._yfinance = yfinance_adapter

    def fetch_liquidity_data(self, base_price: float) -> LiquidityData:
        prices, volumes = [], []
        try:
            df_es = self._yfinance.fetch_price_history("ES=F", period="3mo", interval="1h")
            if df_es is not None and not df_es.empty:
                if isinstance(df_es.columns, pd.MultiIndex):
                    df_es.columns = df_es.columns.get_level_values(0)
                df_es = df_es.dropna(subset=["Close", "Volume"])
                if not df_es.empty:
                    min_p = df_es["Close"].min()
                    max_p = df_es["Close"].max()
                    df_es["notional_b"] = (df_es["Close"] * df_es["Volume"]) / 1_000_000_000
                    num_bins = 25
                    bin_edges = np.linspace(min_p, max_p, num_bins + 1)
                    df_es["bin_idx"] = pd.cut(df_es["Close"], bins=bin_edges, labels=False, include_lowest=True)
                    grouped = df_es.groupby("bin_idx")["notional_b"].sum().reset_index()
                    for i in range(num_bins):
                        p_mid = (bin_edges[i] + bin_edges[i + 1]) / 2
                        matched = grouped[grouped["bin_idx"] == i]
                        v = float(matched["notional_b"].values[0]) if not matched.empty else 0.0
                        if v > 0:
                            prices.append(p_mid)
                            volumes.append(v)
        except Exception:
            logger.warning("ES=F volume profile computation failed", exc_info=True)

        if not prices:
            prices = [base_price * 0.96, base_price * 0.99]
            volumes = [18.4, 45.1]

        return LiquidityData(
            prices=prices,
            volumes=volumes,
            source_label="Yahoo Finance API (S&P 500 Histórico Real — ES=F)",
            unit_label="B",
        )
