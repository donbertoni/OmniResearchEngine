import json
import logging
import os
from typing import Optional

from omni.domain.models import User

logger = logging.getLogger(__name__)


class JsonUserRepository:
    """Fallback local (ver JsonTriggerConfigRepository para o porquê). Suficiente
    para rodar/testar o login localmente sem Postgres; produção deve usar
    PostgresUserRepository."""

    def __init__(self, users_file: str = "users.json"):
        self._users_file = users_file

    def _read_all(self) -> dict:
        if os.path.exists(self._users_file):
            try:
                with open(self._users_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Failed to read users file", exc_info=True)
        return {}

    def create_user(self, email: str, password_hash: str, tier: str) -> User:
        users = self._read_all()
        next_id = (max((u["id"] for u in users.values()), default=0)) + 1
        users[email] = {"id": next_id, "email": email, "password_hash": password_hash, "tier": tier}
        with open(self._users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return User(id=next_id, email=email, password_hash=password_hash, tier=tier)

    def get_by_email(self, email: str) -> Optional[User]:
        data = self._read_all().get(email)
        if not data:
            return None
        return User(id=data["id"], email=data["email"], password_hash=data["password_hash"], tier=data["tier"])

    def update_password_hash(self, user_id: int, new_hash: str) -> None:
        users = self._read_all()
        for email, data in users.items():
            if data["id"] == user_id:
                data["password_hash"] = new_hash
                break
        with open(self._users_file, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
