from omni.application import session_token_service as svc


def test_create_then_verify_round_trips_the_email():
    token = svc.create_token("analista@omni.com")
    assert svc.verify_token(token) == "analista@omni.com"


def test_verify_rejects_tampered_token():
    token = svc.create_token("analista@omni.com")
    tampered = token[:-2] + ("aa" if token[-2:] != "aa" else "bb")
    assert svc.verify_token(tampered) is None


def test_verify_rejects_expired_token():
    token = svc.create_token("analista@omni.com", ttl_seconds=-1)
    assert svc.verify_token(token) is None


def test_verify_rejects_empty_or_garbage_input():
    assert svc.verify_token("") is None
    assert svc.verify_token("not-a-real-token") is None
