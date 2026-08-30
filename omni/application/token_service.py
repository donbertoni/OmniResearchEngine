"""Token de sessão real (JWT RS256) para o mundo multi-tenant -- substitui
`session_token_service.py`, que era um hack deliberadamente documentado como
específico do Streamlit (token assinado dentro de `st.query_params`, sem
revogação, sem conceito de organização/papel).

Ainda não usado por `ui/` (que continua no `session_token_service.py` antigo
até a Fase 1 trocar a UI por FastAPI + Next.js) -- este módulo existe desde a
Fase 0 pra já fixar o formato de claim (`org_id`, `role`, `tier`) que o resto
do sistema multi-tenant depende, sem exigir uma segunda reescrita depois.

RS256 (não HS256) por uma razão concreta: permite publicar só a chave pública
depois (ex: um endpoint JWKS) se algum dia outro serviço precisar validar
tokens sem ter o segredo de assinatura -- sem isso, SSO/OIDC de terceiros
validando esses tokens exigiria redesenhar o formato.
"""

import hashlib
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from typing import Optional

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ACCESS_TOKEN_TTL_SECONDS = 15 * 60
REFRESH_TOKEN_TTL_SECONDS = 30 * 24 * 3600
ALGORITHM = "RS256"

_ephemeral_keys: Optional[tuple] = None


@dataclass(frozen=True)
class TokenClaims:
    sub: str  # user id
    org_id: str
    role: str
    tier: str
    email: str
    jti: str = ""


def _keys() -> tuple:
    """Chaves de assinatura via env var (OMNI_JWT_PRIVATE_KEY/PUBLIC_KEY, PEM).

    Sem elas, gera um par por processo -- válido só o suficiente pra rodar
    localmente sem configurar nada; reiniciar o processo invalida todo token
    emitido antes (mesma limitação documentada, e aceita, em
    session_token_service.py para o segredo HMAC)."""
    env_private = os.environ.get("OMNI_JWT_PRIVATE_KEY")
    env_public = os.environ.get("OMNI_JWT_PUBLIC_KEY")
    if env_private and env_public:
        return env_private, env_public

    global _ephemeral_keys
    if _ephemeral_keys is None:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
        public_pem = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()
        _ephemeral_keys = (private_pem, public_pem)
    return _ephemeral_keys


def issue_access_token(claims: TokenClaims, ttl_seconds: int = ACCESS_TOKEN_TTL_SECONDS) -> str:
    private_pem, _ = _keys()
    now = int(time.time())
    payload = {
        "sub": claims.sub,
        "org_id": claims.org_id,
        "role": claims.role,
        "tier": claims.tier,
        "email": claims.email,
        "jti": claims.jti or str(uuid.uuid4()),
        "iat": now,
        "exp": now + ttl_seconds,
    }
    return jwt.encode(payload, private_pem, algorithm=ALGORITHM)


def verify_access_token(token: str) -> Optional[TokenClaims]:
    _, public_pem = _keys()
    try:
        payload = jwt.decode(token, public_pem, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    required = ("sub", "org_id", "role", "tier", "email")
    if any(field not in payload for field in required):
        return None
    return TokenClaims(
        sub=payload["sub"], org_id=payload["org_id"], role=payload["role"],
        tier=payload["tier"], email=payload["email"], jti=payload.get("jti", ""),
    )


def generate_refresh_token() -> str:
    """Token opaco (não-JWT) -- só o hash é persistido (ver docs/ARCHITECTURE.md,
    tabela `refresh_tokens`); o valor em si nunca é recuperável a partir do
    banco, só comparável via `hash_refresh_token`."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
