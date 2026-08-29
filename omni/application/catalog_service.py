from omni.domain.models import TierPermissions


def determine_tier(login_user: str) -> str:
    login_lower = (login_user or "").lower()
    if "admin" in login_lower or "white" in login_lower:
        return "Premium (B2B White-Label)"
    if "free" in login_lower:
        return "Free (Lead Magnet)"
    return "Standard (B2C Trader)"


def tier_permissions(tier: str) -> TierPermissions:
    allow_customization = "Free" not in tier
    allow_white_label = "Premium" in tier
    if "Standard" in tier:
        max_free_tickers = 5
    elif "Premium" in tier:
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
