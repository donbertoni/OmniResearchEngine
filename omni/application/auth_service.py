"""Autenticação real: senha validada por hash, tier lido do usuário
persistido, não mais inferido por substring do e-mail digitado.

Hash de senha: argon2id (via `argon2-cffi`) para toda senha nova. Hashes
PBKDF2 antigos (formato `"{salt_hex}${derived_hex}"`, sem prefixo) continuam
verificáveis, e são transparentemente re-hasheados para argon2id no primeiro
login bem-sucedido depois desta mudança -- sem forçar reset de senha de
ninguém. Hashes argon2id sempre começam com `$argon2id$` (formato
autodescritivo da própria lib), o que torna a detecção de formato trivial.
"""

import hashlib
import hmac
import os
from typing import Optional, Tuple

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from omni.domain import tiers
from omni.domain.models import User
from omni.domain.ports import UserRepositoryPort

DEFAULT_TIER = tiers.STANDARD
_PBKDF2_ITERATIONS = 260_000
_argon2_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _argon2_hasher.hash(password)


def _is_argon2_hash(stored_hash: str) -> bool:
    return stored_hash.startswith("$argon2")


def _verify_legacy_pbkdf2(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, derived_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return hmac.compare_digest(derived.hex(), derived_hex)


def verify_password(password: str, stored_hash: str) -> bool:
    if _is_argon2_hash(stored_hash):
        try:
            return _argon2_hasher.verify(stored_hash, password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False
    return _verify_legacy_pbkdf2(password, stored_hash)


def register(repo: UserRepositoryPort, email: str, password: str, tier: str = DEFAULT_TIER) -> Tuple[bool, str]:
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        return False, "E-mail inválido."
    if not password or len(password) < 8:
        return False, "Senha deve ter ao menos 8 caracteres."
    if repo.get_by_email(email):
        return False, "Já existe uma conta com esse e-mail."
    repo.create_user(email, hash_password(password), tier)
    return True, "Conta criada com sucesso!"


def authenticate(repo: UserRepositoryPort, email: str, password: str) -> Tuple[Optional[User], str]:
    email = (email or "").strip().lower()
    user = repo.get_by_email(email)
    if not user or not verify_password(password or "", user.password_hash):
        return None, "E-mail ou senha inválidos."
    if not _is_argon2_hash(user.password_hash):
        repo.update_password_hash(user.id, hash_password(password))
    return user, "Login realizado com sucesso!"
