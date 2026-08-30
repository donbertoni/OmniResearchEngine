from omni.domain import tiers
from omni.domain.models import TierPermissions


def tier_permissions(tier: str) -> TierPermissions:
    """Comparação exata contra omni.domain.tiers (não mais substring) -- um
    tier desconhecido ou com typo cai no branch menos privilegiado de forma
    intencional e óbvia, em vez de silenciosamente "quase" bater por
    substring."""
    allow_customization = tier != tiers.FREE
    allow_white_label = tier == tiers.PREMIUM
    if tier == tiers.STANDARD:
        max_free_tickers = 5
    elif tier == tiers.PREMIUM:
        max_free_tickers = 999
    else:
        max_free_tickers = 0
    return TierPermissions(allow_customization, allow_white_label, max_free_tickers)


def add_asset_to_pool(pool: list, name: str, ticker: str, currency: str) -> list:
    if not name or not ticker:
        return pool
    if any(tk == ticker for _, tk, _ in pool):
        return pool
    return pool + [(name, ticker, currency)]


def apply_pool_selection(pool_labels_map: dict, selected_labels: list) -> list:
    return [pool_labels_map[lbl] for lbl in selected_labels if lbl in pool_labels_map]


def upsert_new_category(categories: dict, name: str, tag: str, assets: list) -> dict:
    if name:
        categories[name] = {"tag": tag if tag else "General", "assets": assets}
    return categories


def rename_category(categories: dict, old_name: str, new_name: str) -> str:
    """Renomeia se um novo nome válido foi dado; retorna o nome efetivo da categoria."""
    if new_name and new_name != old_name and old_name in categories:
        categories[new_name] = categories.pop(old_name)
        return new_name
    return old_name


def delete_category(categories: dict, name: str) -> dict:
    categories.pop(name, None)
    return categories


def set_category_assets(categories: dict, name: str, assets: list) -> dict:
    if name in categories:
        categories[name]["assets"] = assets
    return categories
