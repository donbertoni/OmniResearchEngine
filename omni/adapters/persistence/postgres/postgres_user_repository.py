from typing import Optional

from omni.adapters.persistence.postgres.connection import get_connection
from omni.domain.models import User


class PostgresUserRepository:
    def create_user(self, email: str, password_hash: str, tier: str) -> User:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (email, password_hash, tier) VALUES (%s, %s, %s) RETURNING id",
                        (email, password_hash, tier),
                    )
                    user_id = cur.fetchone()[0]
        finally:
            conn.close()
        return User(id=user_id, email=email, password_hash=password_hash, tier=tier)

    def get_by_email(self, email: str) -> Optional[User]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, email, password_hash, tier FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
        finally:
            conn.close()
        if not row:
            return None
        return User(id=row[0], email=row[1], password_hash=row[2], tier=row[3])

    def update_password_hash(self, user_id: int, new_hash: str) -> None:
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
        finally:
            conn.close()
