from omni.application import automation_service
from omni.application.automation_service import AutomationSettings


class FakeAutomationConfigRepository:
    def __init__(self):
        self._data = {}

    def save(self, org_id, config_data):
        self._data[org_id] = config_data
        return True, "ok"

    def load(self, org_id):
        return self._data.get(org_id, {})


class FakeWebhookPort:
    def __init__(self, responses=None):
        self._responses = responses or {}
        self.calls = []

    def post(self, url, payload, auth_token=""):
        self.calls.append((url, payload, auth_token))
        return self._responses.get(url, (True, "delivered"))


def test_save_and_load_round_trip_preserves_fields():
    repo = FakeAutomationConfigRepository()
    settings = AutomationSettings(auto_emails="a@x.com", auto_urls="https://hook/1", crm_platform="HubSpot", crm_api_key="secret")

    automation_service.save_automation_settings(repo, "org-1", settings)
    loaded = automation_service.load_automation_settings(repo, "org-1")

    assert loaded.auto_emails == "a@x.com"
    assert loaded.auto_urls == "https://hook/1"
    assert loaded.crm_api_key == "secret"


def test_orgs_do_not_see_each_others_automation_settings():
    repo = FakeAutomationConfigRepository()
    automation_service.save_automation_settings(repo, "org-1", AutomationSettings(auto_emails="org1@x.com"))
    automation_service.save_automation_settings(repo, "org-2", AutomationSettings(auto_emails="org2@x.com"))

    assert automation_service.load_automation_settings(repo, "org-1").auto_emails == "org1@x.com"
    assert automation_service.load_automation_settings(repo, "org-2").auto_emails == "org2@x.com"


def test_load_falls_back_to_defaults_when_nothing_saved():
    repo = FakeAutomationConfigRepository()
    loaded = automation_service.load_automation_settings(repo, "org-1")
    assert loaded.auto_emails == automation_service.DEFAULT_EMAILS
    assert loaded.auto_urls == ""


def test_dispatch_crm_push_fails_honestly_with_no_urls_configured():
    port = FakeWebhookPort()
    settings = AutomationSettings(auto_urls="")
    results = automation_service.dispatch_crm_push(port, settings, {"foo": "bar"})
    assert results == [("", False, "Nenhuma URL de webhook configurada no painel de Automações.")]
    assert port.calls == []


def test_dispatch_crm_push_posts_to_every_configured_url_with_auth_token():
    port = FakeWebhookPort()
    settings = AutomationSettings(auto_urls="https://hook/a, https://hook/b", crm_platform="RD Station", crm_api_key="tok123")

    results = automation_service.dispatch_crm_push(port, settings, {"foo": "bar"})

    assert [r[0] for r in results] == ["https://hook/a", "https://hook/b"]
    assert all(r[1] is True for r in results)
    assert len(port.calls) == 2
    for url, payload, token in port.calls:
        assert token == "tok123"
        assert payload["crm_platform"] == "RD Station"
        assert payload["foo"] == "bar"


def test_dispatch_crm_push_reports_per_url_failure():
    port = FakeWebhookPort(responses={"https://hook/bad": (False, "HTTP 500")})
    settings = AutomationSettings(auto_urls="https://hook/bad")

    results = automation_service.dispatch_crm_push(port, settings, {})

    assert results == [("https://hook/bad", False, "HTTP 500")]


def test_split_targets_trims_and_drops_empty_entries():
    assert automation_service.split_targets(" a@x.com ,, b@y.com") == ["a@x.com", "b@y.com"]
    assert automation_service.split_targets("") == []
