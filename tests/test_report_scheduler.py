from datetime import datetime
from types import SimpleNamespace

from omni.adapters.scheduling.report_scheduler import check_and_dispatch
from omni.application.automation_service import AutomationSettings
from omni.domain.models import MarketSentiment, Quote

ORG_A = "org-a"
ORG_B = "org-b"


class FakeOrgRepo:
    def __init__(self, org_ids):
        self._org_ids = list(org_ids)

    def list_active_org_ids(self):
        return self._org_ids


class FakeTriggerRepo:
    def __init__(self, configs_by_org):
        self._configs_by_org = configs_by_org
        self.dispatched = []

    def load_all(self, org_id):
        return self._configs_by_org.get(org_id, {})

    def mark_dispatched(self, org_id, modulo, dispatched_at):
        self.dispatched.append((org_id, modulo, dispatched_at))
        self._configs_by_org[org_id][modulo]["last_dispatched_at"] = dispatched_at


class FakeAutomationRepo:
    def __init__(self, settings_by_org=None, default=None):
        self._settings_by_org = settings_by_org or {}
        self._default = default or AutomationSettings()

    def load(self, org_id):
        from dataclasses import asdict
        return asdict(self._settings_by_org.get(org_id, self._default))


class FakeCredentialsRepo:
    def load(self, org_id):
        return {}


class FakeMarketDataPort:
    def fetch_quotes(self, symbols, brapi_token=""):
        return {"BTC-USD": Quote(50000.0, 1.5)}


class FakeSentimentPort:
    def fetch_fear_greed(self):
        return MarketSentiment("70 / 100", "Greed")


class FakeWebhookPort:
    def __init__(self):
        self.calls = []

    def post(self, url, payload, auth_token=""):
        self.calls.append(url)
        return True, "ok"


class FakeEmailPort:
    def __init__(self):
        self.calls = []

    def send(self, to_addresses, subject, body):
        self.calls.append(to_addresses)
        return True, "ok"


class FakeNotificationPort:
    def __init__(self):
        self.calls = []

    def send(self, target, message, credentials):
        self.calls.append(target)
        return True, "ok"


def _build_infra(org_ids, trigger_repo, automation_repo):
    return SimpleNamespace(
        org_repo=FakeOrgRepo(org_ids),
        trigger_repo=trigger_repo,
        automation_repo=automation_repo,
        credentials_repo=FakeCredentialsRepo(),
        market_data_port=FakeMarketDataPort(),
        sentiment_port=FakeSentimentPort(),
        webhook_port=FakeWebhookPort(),
        email_port=FakeEmailPort(),
        whatsapp_port=FakeNotificationPort(),
        telegram_port=FakeNotificationPort(),
        settings=SimpleNamespace(brapi_token="", whatsapp_instance="", whatsapp_token="", telegram_bot_token=""),
    )


def test_dispatches_when_weekday_and_time_match_and_marks_as_dispatched():
    now = datetime(2026, 8, 31, 9, 0)  # Monday 09:00
    trigger_repo = FakeTriggerRepo({
        ORG_A: {"Crypto": {"dias_semana": ["Segunda-feira"], "horarios": ["09:00"], "ativos_selecionados_tickers": ["BTC-USD"]}},
    })
    automation_repo = FakeAutomationRepo({ORG_A: AutomationSettings(auto_emails="a@x.com", auto_urls="https://hook/1")})
    infra = _build_infra([ORG_A], trigger_repo, automation_repo)

    results = check_and_dispatch(now, infra)

    assert len(results) == 1
    assert "Crypto" in results[0]
    assert trigger_repo.dispatched == [(ORG_A, "Crypto", "2026-08-31 09:00")]
    assert infra.email_port.calls == [["a@x.com"]]
    assert infra.webhook_port.calls == ["https://hook/1"]


def test_does_not_dispatch_on_wrong_weekday():
    now = datetime(2026, 8, 30, 9, 0)  # Sunday
    trigger_repo = FakeTriggerRepo({
        ORG_A: {"Crypto": {"dias_semana": ["Segunda-feira"], "horarios": ["09:00"], "ativos_selecionados_tickers": []}},
    })
    infra = _build_infra([ORG_A], trigger_repo, FakeAutomationRepo())

    assert check_and_dispatch(now, infra) == []


def test_does_not_dispatch_twice_in_the_same_minute():
    now = datetime(2026, 8, 31, 9, 0)
    trigger_repo = FakeTriggerRepo({
        ORG_A: {"Crypto": {"dias_semana": ["Segunda-feira"], "horarios": ["09:00"], "ativos_selecionados_tickers": []}},
    })
    infra = _build_infra([ORG_A], trigger_repo, FakeAutomationRepo())

    first = check_and_dispatch(now, infra)
    second = check_and_dispatch(now, infra)

    assert len(first) == 1
    assert second == []


def test_reports_when_no_channel_is_configured():
    now = datetime(2026, 8, 31, 9, 0)
    trigger_repo = FakeTriggerRepo({
        ORG_A: {"Crypto": {"dias_semana": ["Segunda-feira"], "horarios": ["09:00"], "ativos_selecionados_tickers": []}},
    })
    infra = _build_infra([ORG_A], trigger_repo, FakeAutomationRepo(default=AutomationSettings(auto_emails="", auto_urls="")))

    results = check_and_dispatch(now, infra)

    assert "nenhum canal configurado" in results[0]


def test_orgs_are_isolated_from_each_other():
    """Org B's trigger config firing must never touch org A's data, and vice
    versa -- this is the multi-tenant regression this loop exists to prevent."""
    now = datetime(2026, 8, 31, 9, 0)
    trigger_repo = FakeTriggerRepo({
        ORG_A: {"Crypto": {"dias_semana": ["Segunda-feira"], "horarios": ["09:00"], "ativos_selecionados_tickers": []}},
        ORG_B: {"Crypto": {"dias_semana": ["Terça-feira"], "horarios": ["09:00"], "ativos_selecionados_tickers": []}},
    })
    infra = _build_infra([ORG_A, ORG_B], trigger_repo, FakeAutomationRepo())

    results = check_and_dispatch(now, infra)

    assert len(results) == 1
    assert f"org {ORG_A[:8]}" in results[0]
    assert trigger_repo.dispatched == [(ORG_A, "Crypto", "2026-08-31 09:00")]
