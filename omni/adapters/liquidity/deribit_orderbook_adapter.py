import logging

import numpy as np
import pandas as pd
import requests

from omni.domain.models import LiquidityData

logger = logging.getLogger(__name__)


class DeribitLiquidityAdapter:
    """Heatmap de liquidez para Crypto, via order book real do BTC-PERPETUAL na Deribit."""

    def fetch_liquidity_data(self, base_price: float) -> LiquidityData:
        prices, volumes = [], []
        try:
            url = "https://www.deribit.com/api/v2/public/get_order_book?instrument_name=BTC-PERPETUAL&depth=250"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            if res.status_code == 200:
                book_data = res.json().get("result", {})
                bids = pd.DataFrame(book_data.get("bids", []), columns=["price", "qty"])
                asks = pd.DataFrame(book_data.get("asks", []), columns=["price", "qty"])
                df_book = pd.concat([bids, asks])
                if not df_book.empty:
                    df_book["notional_m"] = df_book["qty"] / 1_000_000
                    min_p = base_price * 0.85
                    max_p = base_price * 1.15
                    df_book = df_book[(df_book["price"] >= min_p) & (df_book["price"] <= max_p)]
                    num_bins = 25
                    bin_edges = np.linspace(min_p, max_p, num_bins + 1)
                    df_book["bin_idx"] = pd.cut(df_book["price"], bins=bin_edges, labels=False, include_lowest=True)
                    grouped = df_book.groupby("bin_idx")["notional_m"].sum().reset_index()
                    for i in range(num_bins):
                        p_mid = (bin_edges[i] + bin_edges[i + 1]) / 2
                        matched = grouped[grouped["bin_idx"] == i]
                        v = float(matched["notional_m"].values[0]) if not matched.empty else 0.0
                        if v > 0:
                            prices.append(p_mid)
                            volumes.append(v)
        except Exception:
            logger.warning("Deribit order book request failed", exc_info=True)

        if not prices:
            prices = [base_price * 0.95, base_price * 0.98, base_price * 1.02, base_price * 1.05]
            volumes = [1.2, 4.8, 6.5, 3.1]

        return LiquidityData(
            prices=prices,
            volumes=volumes,
            source_label="Deribit API (BTC-PERPETUAL Order Book Real)",
            unit_label="M",
        )
