from typing import List, Optional

from omni.adapters.persistence.postgres.connection import get_connection
from omni.domain.models import OrgMember


class PostgresOrgMemberRepository:
    def add_member(self, org_id: str, user_id: int, role: str) -> OrgMember:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO org_members (org_id, user_id, role) VALUES (%s, %s, %s)
                        ON CONFLICT (org_id, user_id) DO UPDATE SET role = EXCLUDED.role
                        """,
                        (org_id, user_id, role),
                    )
        finally:
            conn.close()
        return OrgMember(org_id=org_id, user_id=user_id, role=role)

    def get_role(self, org_id: str, user_id: int) -> Optional[str]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT role FROM org_members WHERE org_id = %s AND user_id = %s", (org_id, user_id))
                row = cur.fetchone()
        finally:
            conn.close()
        return row[0] if row else None

    def list_members(self, org_id: str) -> List[OrgMember]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT org_id, user_id, role FROM org_members WHERE org_id = %s", (org_id,))
                rows = cur.fetchall()
        finally:
            conn.close()
        return [OrgMember(org_id=str(r[0]), user_id=r[1], role=r[2]) for r in rows]

    def list_orgs_for_user(self, user_id: int) -> List[OrgMember]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT org_id, user_id, role FROM org_members WHERE user_id = %s", (user_id,))
                rows = cur.fetchall()
        finally:
            conn.close()
        return [OrgMember(org_id=str(r[0]), user_id=r[1], role=r[2]) for r in rows]
