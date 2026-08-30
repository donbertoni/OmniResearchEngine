import hashlib
import hmac
import os

from omni.application import auth_service
from omni.domain.models import User


class FakeUserRepository:
    def __init__(self):
        self._users = {}
        self._next_id = 1

    def create_user(self, email, password_hash, tier):
        user = User(id=self._next_id, email=email, password_hash=password_hash, tier=tier)
        self._users[email] = user
        self._next_id += 1
        return user

    def get_by_email(self, email):
        return self._users.get(email)

    def update_password_hash(self, user_id, new_hash):
        for email, user in self._users.items():
            if user.id == user_id:
                self._users[email] = User(id=user.id, email=user.email, password_hash=new_hash, tier=user.tier)
                return


def _legacy_pbkdf2_hash(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, auth_service._PBKDF2_ITERATIONS)
    return f"{salt.hex()}${derived.hex()}"


def test_register_then_authenticate_succeeds_with_correct_password():
    repo = FakeUserRepository()
    ok, _ = auth_service.register(repo, "Analista@Omni.com", "supersecret123")
    assert ok

    user, msg = auth_service.authenticate(repo, "analista@omni.com", "supersecret123")
    assert user is not None
    assert user.email == "analista@omni.com"
    assert user.tier == auth_service.DEFAULT_TIER


def test_authenticate_fails_with_wrong_password():
    repo = FakeUserRepository()
    auth_service.register(repo, "trader@omni.com", "correcthorsebattery")

    user, msg = auth_service.authenticate(repo, "trader@omni.com", "wrong-password")
    assert user is None
    assert "inválid" in msg.lower()


def test_authenticate_fails_for_unknown_email():
    repo = FakeUserRepository()
    user, msg = auth_service.authenticate(repo, "ghost@omni.com", "whatever123")
    assert user is None


def test_register_rejects_duplicate_email():
    repo = FakeUserRepository()
    auth_service.register(repo, "dup@omni.com", "supersecret123")
    ok, msg = auth_service.register(repo, "dup@omni.com", "anotherpassword")
    assert ok is False


def test_register_rejects_short_password():
    repo = FakeUserRepository()
    ok, msg = auth_service.register(repo, "short@omni.com", "1234")
    assert ok is False


def test_new_passwords_are_hashed_with_argon2id_not_plaintext():
    hashed = auth_service.hash_password("supersecret123")
    assert "supersecret123" not in hashed
    assert hashed.startswith("$argon2id$")
    assert auth_service.verify_password("supersecret123", hashed)
    assert not auth_service.verify_password("wrong", hashed)


def test_malformed_legacy_hash_fails_cleanly_instead_of_crashing():
    repo = FakeUserRepository()
    repo.create_user("corrupted@omni.com", "not-valid-hex$alsonotvalid", auth_service.DEFAULT_TIER)

    user, msg = auth_service.authenticate(repo, "corrupted@omni.com", "whatever123")

    assert user is None
    assert "inválid" in msg.lower()


def test_legacy_pbkdf2_hash_still_verifies():
    legacy_hash = _legacy_pbkdf2_hash("oldpassword123")
    assert not legacy_hash.startswith("$argon2")
    assert auth_service.verify_password("oldpassword123", legacy_hash)
    assert not auth_service.verify_password("wrongpassword", legacy_hash)


def test_login_with_legacy_pbkdf2_hash_transparently_upgrades_to_argon2id():
    repo = FakeUserRepository()
    legacy_hash = _legacy_pbkdf2_hash("oldpassword123")
    repo.create_user("legacy@omni.com", legacy_hash, auth_service.DEFAULT_TIER)

    user, msg = auth_service.authenticate(repo, "legacy@omni.com", "oldpassword123")
    assert user is not None

    upgraded = repo.get_by_email("legacy@omni.com")
    assert upgraded.password_hash.startswith("$argon2id$")

    # e o login continua funcionando normalmente depois do upgrade silencioso
    user2, _ = auth_service.authenticate(repo, "legacy@omni.com", "oldpassword123")
    assert user2 is not None
