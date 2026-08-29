from omni.application.report_service import build_b2b_report
from omni.domain.models import MarketSentiment, Quote


def test_build_b2b_report_skips_disabled_categories_and_assets():
    categories = {
        "Cat A": {"tag": "TagA", "assets": [("Bitcoin", "BTC-USD", "$"), ("Ethereum", "ETH-USD", "$")]},
        "Cat B": {"tag": "TagB", "assets": [("Ouro", "GC=F", "$")]},
    }
    quotes = {"BTC-USD": Quote(50000.0, 2.5), "ETH-USD": Quote(3000.0, -1.0)}
    sentiment = MarketSentiment("70 / 100", "Greed")

    enabled_categories = {"Cat A"}
    enabled_assets = {("Cat A", "BTC-USD")}

    report = build_b2b_report(
        "Crypto", "OMNI", "CNPI-T 0000", "27/08/2026 às 10:00:00 BRT", "PT", sentiment,
        categories, quotes,
        is_category_enabled=lambda cat: cat in enabled_categories,
        is_asset_enabled=lambda cat, ticker: (cat, ticker) in enabled_assets,
    )

    assert "CAT A" in report
    assert "Bitcoin" in report
    assert "Ethereum" not in report
    assert "CAT B" not in report


def test_build_b2b_report_includes_sentiment_and_header_fields():
    sentiment = MarketSentiment("81 / 100", "Greed")
    report = build_b2b_report(
        "TradFi (Macro)", "OMNI", "CNPI-T 0000", "27/08/2026 às 10:00:00 BRT", "PT", sentiment,
        {}, {},
        is_category_enabled=lambda cat: True,
        is_asset_enabled=lambda cat, ticker: True,
    )
    assert "TRADFI (MACRO)" in report
    assert "81 / 100 (Greed)" in report
