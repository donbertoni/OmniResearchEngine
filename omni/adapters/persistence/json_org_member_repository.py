import json
import logging
import os
from typing import List, Optional

from omni.domain.models import OrgMember

logger = logging.getLogger(__name__)


class JsonOrgMemberRepository:
    """Fallback local (ver JsonTriggerConfigRepository para o porquê)."""

    def __init__(self, members_file: str = "org_members.json"):
        self._members_file = members_file

    def _read_all(self) -> list:
        if os.path.exists(self._members_file):
            try:
                with open(self._members_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read org members file", exc_info=True)
        return []

    def _write_all(self, data: list) -> None:
        with open(self._members_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_member(self, org_id: str, user_id: int, role: str) -> OrgMember:
        members = self._read_all()
        for m in members:
            if m["org_id"] == org_id and m["user_id"] == user_id:
                m["role"] = role
                self._write_all(members)
                return OrgMember(org_id=org_id, user_id=user_id, role=role)
        members.append({"org_id": org_id, "user_id": user_id, "role": role})
        self._write_all(members)
        return OrgMember(org_id=org_id, user_id=user_id, role=role)

    def get_role(self, org_id: str, user_id: int) -> Optional[str]:
        for m in self._read_all():
            if m["org_id"] == org_id and m["user_id"] == user_id:
                return m["role"]
        return None

    def list_members(self, org_id: str) -> List[OrgMember]:
        return [OrgMember(**m) for m in self._read_all() if m["org_id"] == org_id]

    def list_orgs_for_user(self, user_id: int) -> List[OrgMember]:
        return [OrgMember(**m) for m in self._read_all() if m["user_id"] == user_id]
