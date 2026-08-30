from omni.application import token_service
from omni.application.token_service import TokenClaims


def _claims(**overrides):
    base = dict(sub="1", org_id="org-1", role="owner", tier="Standard (B2C Trader)", email="a@x.com")
    base.update(overrides)
    return TokenClaims(**base)


def test_issue_then_verify_round_trips_all_claims():
    token = token_service.issue_access_token(_claims())
    claims = token_service.verify_access_token(token)
    assert claims is not None
    assert claims.sub == "1"
    assert claims.org_id == "org-1"
    assert claims.role == "owner"
    assert claims.tier == "Standard (B2C Trader)"
    assert claims.email == "a@x.com"


def test_verify_rejects_expired_token():
    token = token_service.issue_access_token(_claims(), ttl_seconds=-1)
    assert token_service.verify_access_token(token) is None


def test_verify_rejects_garbage_token():
    assert token_service.verify_access_token("not-a-jwt") is None
    assert token_service.verify_access_token("") is None


def test_refresh_token_is_opaque_and_hash_is_deterministic():
    token = token_service.generate_refresh_token()
    assert len(token) > 20
    h1 = token_service.hash_refresh_token(token)
    h2 = token_service.hash_refresh_token(token)
    assert h1 == h2
    assert token not in h1


def test_different_refresh_tokens_hash_differently():
    a = token_service.hash_refresh_token(token_service.generate_refresh_token())
    b = token_service.hash_refresh_token(token_service.generate_refresh_token())
    assert a != b
