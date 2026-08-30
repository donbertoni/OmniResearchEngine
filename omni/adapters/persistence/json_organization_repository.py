import json
import logging
import os
import uuid
from typing import List, Optional

from omni.domain.models import Organization
from omni.domain.tenancy import LEGACY_ORG_ID

logger = logging.getLogger(__name__)

_LEGACY_ORG_SEED = {
    "id": LEGACY_ORG_ID,
    "name": "Legacy (Streamlit)",
    "slug": "legacy-streamlit",
    "tier": "Standard (B2C Trader)",
    "subscription_status": "trialing",
    "stripe_customer_id": "",
    "stripe_subscription_id": "",
    "company_name": "",
    "cnpi_code": "",
    "logo_url": "",
    "primary_color": "",
    "custom_domain": "",
}


class JsonOrganizationRepository:
    """Fallback local (ver JsonTriggerConfigRepository para o porquê). Sempre
    contém pelo menos a organização legado (LEGACY_ORG_ID), criada sob demanda,
    para que ui/ funcione sem exigir Postgres."""

    def __init__(self, orgs_file: str = "organizations.json"):
        self._orgs_file = orgs_file

    def _read_all(self) -> dict:
        if os.path.exists(self._orgs_file):
            try:
                with open(self._orgs_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read organizations file", exc_info=True)
        return {LEGACY_ORG_ID: dict(_LEGACY_ORG_SEED)}

    def _write_all(self, data: dict) -> None:
        with open(self._orgs_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def create_organization(self, name: str, slug: str, tier: str) -> Organization:
        org_id = str(uuid.uuid4())
        orgs = self._read_all()
        orgs[org_id] = {**_LEGACY_ORG_SEED, "id": org_id, "name": name, "slug": slug, "tier": tier}
        self._write_all(orgs)
        return Organization(id=org_id, name=name, slug=slug, tier=tier)

    def get_by_id(self, org_id: str) -> Optional[Organization]:
        data = self._read_all().get(org_id)
        return Organization(**data) if data else None

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        for data in self._read_all().values():
            if data["slug"] == slug:
                return Organization(**data)
        return None

    def update(self, org_id: str, fields: dict) -> None:
        orgs = self._read_all()
        if org_id in orgs:
            orgs[org_id].update(fields)
            self._write_all(orgs)

    def list_active_org_ids(self) -> List[str]:
        return [org_id for org_id, data in self._read_all().items() if data.get("subscription_status") != "canceled"]
