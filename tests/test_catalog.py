from omni.application.catalog_service import determine_tier, tier_permissions
from omni.domain.catalog import CATEGORIES_CRYPTO, build_initial_asset_pool


def test_build_initial_asset_pool_dedupes_by_ticker():
    categories = {
        "A": {"tag": "A", "assets": [("Bitcoin", "BTC-USD", "$"), ("Ethereum", "ETH-USD", "$")]},
        "B": {"tag": "B", "assets": [("Bitcoin Again", "BTC-USD", "$")]},
    }
    pool = build_initial_asset_pool(categories)
    tickers = [tk for _, tk, _ in pool]
    assert tickers == ["BTC-USD", "ETH-USD"]


def test_build_initial_asset_pool_from_real_crypto_catalog_has_no_duplicate_tickers():
    pool = build_initial_asset_pool(CATEGORIES_CRYPTO)
    tickers = [tk for _, tk, _ in pool]
    assert len(tickers) == len(set(tickers))


def test_determine_tier_admin_and_white_are_premium():
    assert determine_tier("admin@omni.com") == "Premium (B2B White-Label)"
    assert determine_tier("whitelabel@gestora.com") == "Premium (B2B White-Label)"


def test_determine_tier_free_is_lead_magnet():
    assert determine_tier("free@omni.com") == "Free (Lead Magnet)"


def test_determine_tier_default_is_standard():
    assert determine_tier("analista@omni.com") == "Standard (B2C Trader)"


def test_tier_permissions_standard_limits_to_five_tickers():
    perms = tier_permissions("Standard (B2C Trader)")
    assert perms.max_free_tickers == 5
    assert perms.allow_customization is True
    assert perms.allow_white_label is False


def test_tier_permissions_free_has_no_customization_or_tickers():
    perms = tier_permissions("Free (Lead Magnet)")
    assert perms.allow_customization is False
    assert perms.max_free_tickers == 0


def test_tier_permissions_premium_allows_white_label():
    perms = tier_permissions("Premium (B2B White-Label)")
    assert perms.allow_white_label is True
    assert perms.max_free_tickers == 999
