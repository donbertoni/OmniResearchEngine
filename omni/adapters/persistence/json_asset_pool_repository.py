import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class JsonAssetPoolRepository:
    """Fallback local (ver JsonTriggerConfigRepository para o porquê).
    Arquivos aninhados por `org_id` e depois por `modulo`."""

    def __init__(self, pools_file: str = "asset_pools.json", categories_file: str = "asset_categories.json"):
        self._pools_file = pools_file
        self._categories_file = categories_file

    def _read(self, path: str) -> dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read %s", path, exc_info=True)
        return {}

    def _write(self, path: str, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_pool(self, org_id: str, modulo: str) -> Optional[list]:
        data = self._read(self._pools_file).get(org_id, {}).get(modulo)
        return [tuple(item) for item in data] if data is not None else None

    def save_pool(self, org_id: str, modulo: str, pool: list) -> None:
        all_pools = self._read(self._pools_file)
        all_pools.setdefault(org_id, {})[modulo] = pool
        self._write(self._pools_file, all_pools)

    def load_categories(self, org_id: str, modulo: str) -> Optional[dict]:
        data = self._read(self._categories_file).get(org_id, {}).get(modulo)
        if data is None:
            return None
        for cat_info in data.values():
            cat_info["assets"] = [tuple(a) for a in cat_info["assets"]]
        return data

    def save_categories(self, org_id: str, modulo: str, categories: dict) -> None:
        all_categories = self._read(self._categories_file)
        all_categories.setdefault(org_id, {})[modulo] = categories
        self._write(self._categories_file, all_categories)
