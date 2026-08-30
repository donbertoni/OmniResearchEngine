import uuid
from typing import List, Optional

from omni.adapters.persistence.postgres.connection import get_connection
from omni.domain.models import Organization

_COLUMNS = (
    "id, name, slug, tier, subscription_status, stripe_customer_id, "
    "stripe_subscription_id, company_name, cnpi_code, logo_url, primary_color, custom_domain"
)
_UPDATABLE_COLUMNS = {
    "name", "slug", "tier", "subscription_status", "stripe_customer_id", "stripe_subscription_id",
    "company_name", "cnpi_code", "logo_url", "primary_color", "custom_domain",
}


def _row_to_org(row) -> Organization:
    return Organization(
        id=str(row[0]), name=row[1], slug=row[2], tier=row[3], subscription_status=row[4],
        stripe_customer_id=row[5] or "", stripe_subscription_id=row[6] or "",
        company_name=row[7] or "", cnpi_code=row[8] or "", logo_url=row[9] or "",
        primary_color=row[10] or "", custom_domain=row[11] or "",
    )


class PostgresOrganizationRepository:
    def create_organization(self, name: str, slug: str, tier: str) -> Organization:
        org_id = str(uuid.uuid4())
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO organizations (id, name, slug, tier) VALUES (%s, %s, %s, %s)",
                        (org_id, name, slug, tier),
                    )
        finally:
            conn.close()
        return Organization(id=org_id, name=name, slug=slug, tier=tier)

    def get_by_id(self, org_id: str) -> Optional[Organization]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {_COLUMNS} FROM organizations WHERE id = %s", (org_id,))
                row = cur.fetchone()
        finally:
            conn.close()
        return _row_to_org(row) if row else None

    def get_by_slug(self, slug: str) -> Optional[Organization]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {_COLUMNS} FROM organizations WHERE slug = %s", (slug,))
                row = cur.fetchone()
        finally:
            conn.close()
        return _row_to_org(row) if row else None

    def update(self, org_id: str, fields: dict) -> None:
        if not fields:
            return
        unknown = set(fields) - _UPDATABLE_COLUMNS
        if unknown:
            raise ValueError(f"Cannot update unknown organization column(s): {sorted(unknown)}")
        set_clause = ", ".join(f"{col} = %s" for col in fields)
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"UPDATE organizations SET {set_clause}, updated_at = now() WHERE id = %s",
                        (*fields.values(), org_id),
                    )
        finally:
            conn.close()

    def list_active_org_ids(self) -> List[str]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM organizations WHERE subscription_status != 'canceled'")
                rows = cur.fetchall()
        finally:
            conn.close()
        return [str(r[0]) for r in rows]
