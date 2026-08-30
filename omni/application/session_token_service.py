"""Implementa de verdade o "Manter-se conectado", que antes era um checkbox
puramente decorativo (nenhuma persistência além do que o próprio Streamlit já
faz para a aba do navegador).

Um token HMAC assinado (e-mail + expiração) é guardado em st.query_params
pelo chamador; verify_token confirma a assinatura e a validade antes de logar
automaticamente. Sem dependência nova (só stdlib hmac/hashlib).

Limite real (documentado, não escondido): a assinatura usa um segredo por
processo quando OMNI_SESSION_SECRET não está definida, então reiniciar o
processo Python invalida sessões "mantidas conectadas" -- para persistir entre
deploys/restarts, defina OMNI_SESSION_SECRET. E como o token vive na URL (não
em um cookie), ele só sobrevive na mesma aba/link, não em qualquer navegador
do mesmo usuário.
"""

import base64
import hashlib
import hmac
import os
import time
from typing import Optional

_TOKEN_TTL_SECONDS = 30 * 24 * 3600


def _secret() -> str:
    env_secret = os.environ.get("OMNI_SESSION_SECRET")
    if env_secret:
        return env_secret
    global _PROCESS_SECRET
    try:
        return _PROCESS_SECRET
    except NameError:
        _PROCESS_SECRET = base64.urlsafe_b64encode(os.urandom(32)).decode()
        return _PROCESS_SECRET


def create_token(email: str, ttl_seconds: int = _TOKEN_TTL_SECONDS) -> str:
    expiry = int(time.time()) + ttl_seconds
    payload = f"{email}:{expiry}"
    sig = hmac.new(_secret().encode(), payload.encode(), hashlib.sha256).hexdigest()
    raw = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def verify_token(token: str) -> Optional[str]:
    if not token:
        return None
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        email, expiry_str, sig = raw.rsplit(":", 2)
        expiry = int(expiry_str)
    except Exception:
        return None
    if time.time() > expiry:
        return None
    expected_sig = hmac.new(_secret().encode(), f"{email}:{expiry}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None
    return email
