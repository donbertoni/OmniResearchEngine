import logging

import requests

from omni.domain.models import MarketSentiment

logger = logging.getLogger(__name__)


class AlternativeMeSentimentAdapter:
    def fetch_fear_greed(self) -> MarketSentiment:
        try:
            res = requests.get("https://api.alternative.me/fng/", timeout=3)
            if res.status_code == 200:
                data = res.json()["data"][0]
                return MarketSentiment(data.get("value", "62") + " / 100", data.get("value_classification", "Greed"))
        except Exception:
            logger.warning("Alternative.me Fear & Greed request failed", exc_info=True)
        return MarketSentiment("62 / 100", "Greed")
