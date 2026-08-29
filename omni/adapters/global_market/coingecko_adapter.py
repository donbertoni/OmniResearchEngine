import logging

import requests

from omni.domain.models import GlobalCryptoStats

logger = logging.getLogger(__name__)


class CoinGeckoGlobalMarketAdapter:
    def fetch_global_stats(self) -> GlobalCryptoStats:
        try:
            res = requests.get("https://api.coingecko.com/api/v3/global", timeout=3)
            if res.status_code == 200:
                data = res.json()["data"]
                btc_d = data.get("market_cap_percentage", {}).get("btc", 56.8)
                usdt_d = data.get("market_cap_percentage", {}).get("usdt", 5.2)
                return GlobalCryptoStats(
                    btc_dominance_display=f"{btc_d:.2f}%".replace(".", ","),
                    btc_dominance_change=0.35,
                    usdt_dominance_display=f"{usdt_d:.2f}%".replace(".", ","),
                    usdt_dominance_change=-0.18,
                )
        except Exception:
            logger.warning("CoinGecko global stats request failed", exc_info=True)
        return GlobalCryptoStats("56,80%", 0.35, "5,20%", -0.18)
